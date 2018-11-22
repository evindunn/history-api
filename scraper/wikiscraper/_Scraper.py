import multiprocessing as mp
import os
import pymysql
import re
import requests
import sys
import threading
import time
from bs4 import BeautifulSoup

# For testing without installing the module
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from wikiscraper.utils import URLBuilder, DBUtils, MonthLookup


class Scraper:
    PROTOCOL = "https"
    HOST_WIKIPEDIA = "en.wikipedia.org"
    PATH_WIKI = "wiki"
    PARSER = "lxml"
    TYPE_EVENT = "Events"
    TYPE_BIRTH = "Births"
    TYPE_DEATH = "Deaths"
    TAG_LINK = 'a'
    DATABASE_NAME = "history.db"
    TABLE_EVENTS = "events"
    TABLE_LINKS = "links"
    TABLE_IMAGES = "images"
    DAYS_IN_YEAR = MonthLookup.generate_days_in_year()

    DB_HOST = os.environ["DB_HOST"]
    DB_USER = os.environ["DB_USER"]
    DB_PASS = os.environ["DB_PASS"]
    DB_NAME = "history"
    DB_CURSOR_CLASS = pymysql.cursors.DictCursor

    # Build our wikipedia url
    WIKI_BASE_URL = URLBuilder().protocol(
        PROTOCOL
    ).hostname(
        HOST_WIKIPEDIA
    ).path_segment(
        PATH_WIKI
    ).build()

    def __init__(self):
        self.done = False
        self.start_tick = int(time.time())
        self.month_lookup = MonthLookup()

        manager = mp.Manager()
        self.lock = manager.Lock()
        self.inserted_queue = manager.Queue()
        self.current_day_queue = manager.Queue()

        self.inserted = 0
        self.current_day = str()

        db_connection = pymysql.connect(
            Scraper.DB_HOST,
            Scraper.DB_USER,
            Scraper.DB_PASS,
            Scraper.DB_NAME
        )
        DBUtils.drop_table(db_connection, Scraper.TABLE_EVENTS)
        DBUtils.drop_table(db_connection, Scraper.TABLE_LINKS)
        DBUtils.drop_table(db_connection, Scraper.TABLE_IMAGES)
        DBUtils.create_table(
            db_connection,
            Scraper.TABLE_EVENTS,
            _id="BIGINT(64) UNSIGNED PRIMARY KEY AUTO_INCREMENT",
            year="INT(11) NOT NULL",
            era="CHAR(4) NOT NULL",
            month="INT(8) NOT NULL",
            day="INT(5) NOT NULL",
            text="TEXT(512) NOT NULL",
            type="CHAR(8) NOT NULL"
        )
        DBUtils.create_table(
            db_connection,
            Scraper.TABLE_LINKS,
            _id="BIGINT(64) UNSIGNED PRIMARY KEY AUTO_INCREMENT",
            event_id="BIGINT(64) UNSIGNED NOT NULL",
            text="TEXT(256) NOT NULL",
            href="TEXT(256) NOT NULL"
        )
        DBUtils.create_table(
            db_connection,
            Scraper.TABLE_IMAGES,
            _id="BIGINT(64) UNSIGNED PRIMARY KEY AUTO_INCREMENT",
            link_id="BIGINT(64) UNSIGNED NOT NULL",
            href="TEXT(256) NOT NULL"
        )
        db_connection.close()

    def run(self):
        threading.Thread(target=self.print_status).start()
        threading.Thread(target=self.poll_queues).start()
        with mp.Pool() as p:
            p.map(
                self.process_day,
                Scraper.DAYS_IN_YEAR,
                chunksize=5
            )
        self.done = True

    def process_day(self, day):
        db_connection = None
        try:
            db_connection = pymysql.connect(
                Scraper.DB_HOST,
                Scraper.DB_USER,
                Scraper.DB_PASS,
                Scraper.DB_NAME,
                cursorclass=Scraper.DB_CURSOR_CLASS
            )

            day_url = "{}/{}".format(Scraper.WIKI_BASE_URL, day)
            req_content = requests.get(day_url).content
            req_doc = BeautifulSoup(req_content, Scraper.PARSER)
            month, day_int = day.split("_", maxsplit=1)
            month = self.month_lookup[month]
            day_int = int(day_int)

            # Get the html lists for events, births, and deaths
            events_list = req_doc.find(
                id=Scraper.TYPE_EVENT
            ).find_parent().find_next_sibling()

            births_list = req_doc.find(
                id=Scraper.TYPE_BIRTH
            ).find_parent().find_next_sibling()

            deaths_list = req_doc.find(
                id=Scraper.TYPE_DEATH
            ).find_parent().find_next_sibling()

            # For each event, extract the year, the text, and any embedded links
            for t in [Scraper.TYPE_EVENT, Scraper.TYPE_BIRTH, Scraper.TYPE_DEATH]:
            # for t in [Scraper.TYPE_EVENT]:

                # Choose the right list to parse based upon event type
                if t == Scraper.TYPE_EVENT:
                    element = events_list
                elif t == Scraper.TYPE_BIRTH:
                    element = births_list
                elif t == Scraper.TYPE_DEATH:
                    element = deaths_list
                else:
                    continue

                # Parse events
                for event in element.children:
                    if not isinstance(event, str):
                        event_text = event.get_text()
                    else:
                        event_text = event
                    event_text = event_text.strip()
                    if event_text is "":
                        continue

                    try:
                        year, text = re.split(
                            " [-\\u2013] ",
                            event_text,
                            maxsplit=1
                        )
                        era = re.search("[A-Za-z]+", year)
                        if era is None:
                            era = "AD"
                        else:
                            era = era.group(0)
                        if era in year:
                            year = year.replace(era, '')
                        year = int(year.strip())
                    except ValueError:
                        continue
                    text = text.strip()

                    # Add the event
                    DBUtils.insert(
                        db_connection,
                        self.TABLE_EVENTS,
                        year=year,
                        era=era,
                        month=month,
                        day=day_int,
                        text=text,
                        type=t
                    )
                    self.current_day_queue.put(
                        "{}".format(day.replace("_", " "))
                    )
                    self.inserted_queue.put(1)

                    event_id = DBUtils.query(
                        db_connection,
                        Scraper.TABLE_EVENTS,
                        ["_id"],
                        "text='{}'".format(text.replace("'", "''"))
                    )

                    # Grab the links associated with the event
                    if event_id is not None:
                        event_id = event_id[0]["_id"]
                        event_embedded_links = Scraper.get_embedded_links(event)
                        for href, text in event_embedded_links:
                            DBUtils.insert(
                                db_connection,
                                Scraper.TABLE_LINKS,
                                event_id=event_id,
                                href=href,
                                text=text
                            )

                            link_id = DBUtils.query(
                                db_connection,
                                Scraper.TABLE_LINKS,
                                ["_id"],
                                "href='{}'".format(
                                    href.format(text.replace("'", "''"))
                                )
                            )

                            if link_id is not None:
                                link_id = link_id[0]["_id"]
                                # Grab the primary image for the link, if any
                                image = Scraper.get_wiki_page_image(href)
                                if image is not None:
                                    DBUtils.insert(
                                        db_connection,
                                        Scraper.TABLE_IMAGES,
                                        link_id=link_id,
                                        href=image
                                    )

        except Exception as e:
            print(
                "\033[31mProcessing {} failed: {}\033[m".format(
                    day.replace("_", " "),
                    e
                ),
                file=sys.stderr
            )
        finally:
            if db_connection is not None:
                db_connection.close()

    @staticmethod
    def process_links(db_connection, event_id, event_embedded_links):
        pass

    @staticmethod
    def get_embedded_links(element):
        """
        :param element: A BeautifulSoup object
        :return: The a link from the object, in the form
        ([link text], [link href])
        """
        try:
            embedded_links = list()
            links = element.findAll(Scraper.TAG_LINK)
            if links is None:
                return None
            for link in links:
                text = link.getText()
                href = re.sub(
                    '^',
                    "{}://{}".format(Scraper.PROTOCOL, Scraper.HOST_WIKIPEDIA),
                    link["href"].replace("'", "''")
                )
                embedded_links.append([href, text])
                # print("{}: {}".format(text, href))
        except Exception as e:
            # print("\n\033[31m{}\033[m".format(e), file=sys.stderr)
            embedded_links = None
        return embedded_links

    @staticmethod
    def get_wiki_page_image(url):
        """
        :param url: The url to a wikipedia page
        :return: The url for the 'main' image on the given wikipedia page
        """
        try:
            link_content = requests.get(url).content
            link_doc = BeautifulSoup(link_content, Scraper.PARSER)
            image = link_doc.find(
                class_="vcard"
            ).find(
                class_="image"
            ).find(
                "img"
            )
            image = re.sub(
                '^',
                "{}:".format(Scraper.PROTOCOL),
                image["src"]
            )
            # print("Image: {}".format(image))
        except Exception as e:
            # print("\n{}".format(e), file=sys.stderr)
            image = None
        return image

    def poll_queues(self):
        while not self.done:
            if not self.inserted_queue.empty():
                with self.lock:
                    self.inserted += self.inserted_queue.get()
            if not self.current_day_queue.empty():
                with self.lock:
                    self.current_day = self.current_day_queue.get()

    def print_status(self):
        while not self.done:
            with self.lock:
                inserted = self.inserted
                current_day = self.current_day

            seconds = int(time.time() - self.start_tick)

            hours = seconds // 60**2
            minutes = seconds // 60 % 60

            if seconds == 0:
                speed = 0
            else:
                speed = round(inserted / seconds, 1)

            # Print the current message
            print(
                "Current Day:       {}".format(current_day),
                end="\033[K\n",
                flush=True
            )
            print(
                "Events Inserted:   {}".format(inserted),
                end="\033[K\n",
                flush=True
            )
            print(
                "Average Speed:     {} events/sec".format(speed),
                end="\033[K\n",
                flush=True
            )
            print(
                "Running for {} hours {} minutes {} seconds".format(
                    hours,
                    minutes,
                    seconds % 60
                ),
                end="\033[K",
                flush=True
            )

            # Go up 4 lines before printing the next message
            print("\033[4A")
            time.sleep(1)

        # Go down 4 lines when done
        print("\033[4B")
