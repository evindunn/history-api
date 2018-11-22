import sys


class DBUtils:
    _SQL_CREATE_TABLE = "CREATE TABLE IF NOT EXISTS {}({});"
    _SQL_DROP_TABLE = "DROP TABLE IF EXISTS {};"
    _SQL_INSERT = "INSERT INTO {}({}) VALUES({});"
    _SQL_QUERY = "SELECT {} FROM {} WHERE {};"
    _SQL_QUERY_ALL = "SELECT {} FROM {};"
    _SQL_SELECT_MAX = "SELECT MAX({}) FROM {};"

    # _LOCK = mp.Lock()

    @staticmethod
    def create_table(db_connection, table_name, **kwargs):
        try:
            with db_connection.cursor() as cursor:
                columns = ["{} {}".format(k, v) for k, v in kwargs.items()]
                sql = DBUtils._SQL_CREATE_TABLE.format(
                    table_name,
                    ", ".join(columns)
                )
                cursor.execute(sql)
        except Exception as e:
            print(
                "\033[31mCreate table failed: {}\033[m".format(e),
                file=sys.stderr
            )
            db_connection.rollback()
        else:
            db_connection.commit()

    @staticmethod
    def drop_table(db_connection, table_name):
        try:
            with db_connection.cursor() as cursor:
                sql = DBUtils._SQL_DROP_TABLE.format(table_name)
                cursor.execute(sql)
        except Exception as e:
            print(
                "\033[31mDrop Table failed {}\033[m".format(e),
                file=sys.stderr
            )
            db_connection.rollback()
        else:
            db_connection.commit()

    @staticmethod
    def insert(db_connection, table_name, **kwargs):
        try:
            with db_connection.cursor() as cursor:
                vals = list()
                for v in kwargs.values():
                    if isinstance(v, str):
                        v = "'{}'".format(v.replace("'", "''"))
                    else:
                        v = str(v)
                    vals.append(v)
                sql = DBUtils._SQL_INSERT.format(
                    table_name,
                    ", ".join(kwargs.keys()),
                    ", ".join(vals)
                )
                # with DBUtils._LOCK:
                #     print(sql)
                cursor.execute(sql)
        except Exception as e:
            print(
                "\033[31mInsert failed: {}\033[m".format(e),
                file=sys.stderr
            )
            db_connection.rollback()
        else:
            db_connection.commit()

    @staticmethod
    def query(db_connection, table_name, columns=None, where_clause=None):
        with db_connection.cursor() as cursor:
            if columns is None:
                columns = '*'
            else:
                columns = ", ".join(columns)
            if where_clause is not None:
                q = DBUtils._SQL_QUERY.format(
                    columns,
                    table_name,
                    where_clause
                )
            else:
                q = DBUtils._SQL_QUERY_ALL.format(columns, table_name)
            # with DBUtils._LOCK:
            #     print(q)
            try:
                cursor.execute(q)
                res = cursor.fetchall()
            except Exception as e:
                print(
                    "\033[31mQuery failed: {} - {}\033[m".format(q, e),
                    file=sys.stderr
                )
                res = None
            if len(res) == 0:
                res = None
        return res

    @staticmethod
    def max_column(db_connection, table_name, column_name):
        with db_connection.cursor() as cursor:
            try:
                sql = DBUtils._SQL_SELECT_MAX.format(column_name, table_name)
                cursor.execute(sql)
                m = cursor.fetchone()["MAX({})".format(column_name)]
            except Exception as e:
                print(
                    "\033[31mMAX() failed: {}\033[m".format(e),
                    file=sys.stderr
                )
                m = None
        return m
