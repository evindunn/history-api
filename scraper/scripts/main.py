#!/usr/bin/env python3

import sys

sys.path.insert(0, ".")     # For testing without installing the module
from wikiscraper import Scraper


def main():
    Scraper().run()


if __name__ == "__main__":
    main()
