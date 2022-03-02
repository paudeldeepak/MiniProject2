import sqlite3
import time
import hashlib


def setupDatabase(path="miniproj2.db"):
    print(path)
    print("created database at path:", path)
    connect(path)
    connection.close()


def connect(path):
    global connection, cursor
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    with open('prj-tables.sql') as fp:
        cursor.executescript(fp.read())
    connection.commit()
    return connection, cursor

if __name__ == '__main__':
    setupDatabase()
