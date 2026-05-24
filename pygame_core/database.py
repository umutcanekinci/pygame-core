import sqlite3
import sys
import os


class Database:
    def __init__(self, name):
        self.name = name
        self.connection: sqlite3.Connection | None = None

    def connect(self) -> bool:
        try:
            if not os.path.exists("databases"):
                os.makedirs("databases")
                print("==> Created databases folder!")

            self.connection = sqlite3.connect(("databases/" + self.name + ".db"))
        except Exception as error:
            print("==> Failed to connect to database!", error)
            return False
        else:
            return True

    def get_cursor(self):
        assert self.connection is not None, "Database not connected"
        return self.connection.cursor()

    def execute_safely(self, query: str, fetch: bool = False, *, params: tuple = ()) -> list[tuple] | None:
        if not self.connect():
            return sys.exit()

        cursor = self.execute(query, params)
        result = cursor.fetchall() if fetch else None

        self.commit()
        self.disconnect()

        return result

    def execute(self, sql, params: tuple = ()):
        try:
            return self.get_cursor().execute(sql, params)
        except Exception as error:
            print("An error occured during execute sql code:", error)
            return sys.exit()

    def commit(self):
        assert self.connection is not None, "Database not connected"
        self.connection.commit()

    def disconnect(self):
        assert self.connection is not None, "Database not connected"
        self.connection.close()