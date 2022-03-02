import genericpath
import sqlite3
import os.path
from os import path
import time
import hashlib
import logging


def connect(path):
    global connection, cursor

    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute(' PRAGMA foreign_keys=ON; ')
    connection.commit()
    return

def drop_tables():
    global connection, cursor

    drop_editor = "DROP TABLE IF EXISTS editors;"
    drop_follows = "DROP TABLE IF EXISTS follows;"
    drop_watch = "DROP TABLE IF EXISTS watch;"
    drop_sessions = "DROP TABLE IF EXISTS sessions;"
    drop_customers = "DROP TABLE IF EXISTS customers;"
    drop_recommendations = "DROP TABLE IF EXISTS recommendations;"
    drop_casts = "DROP TABLE IF EXISTS casts;"
    drop_movies = "DROP TABLE IF EXISTS movies;"
    drop_moviePeople = "DROP TABLE IF EXISTS moviePeople;"

    cursor.execute(drop_editor)
    cursor.execute(drop_follows)
    cursor.execute(drop_watch)
    cursor.execute(drop_sessions)
    cursor.execute(drop_customers)
    cursor.execute(drop_recommendations)
    cursor.execute(drop_casts)
    cursor.execute(drop_movies)
    cursor.execute(drop_moviePeople)

def define_tables():
    global connection, cursor

    moviePeople_query = '''
                        create table moviePeople (
                            pid		char(4),
                            name		text,
                            birthYear	int,
                            primary key (pid)
                        );
                    '''

    movies_query = '''
                        create table movies (
                            mid		int,
                            title		text,
                            year		int,
                            runtime	int,
                            primary key (mid)
                        );
                    '''

    casts_query = '''
                        create table casts (
                            mid		int,
                            pid		char(4),
                            role		text,
                            primary key (mid,pid),
                            foreign key (mid) references movies,
                            foreign key (pid) references moviePeople
                        );
                    '''

    recommendations_query = '''
                        create table recommendations (
                            watched	int,
                            recommended	int,
                            score		float,
                            primary key (watched,recommended),
                            foreign key (watched) references movies,
                            foreign key (recommended) references movies
                        );
                    '''
    
    customers_query = '''
                        create table customers (
                            cid		char(4),
                            name		text,
                            pwd		text,
                            primary key (cid)
                        );
                    '''

    sessions_query = '''
                        create table sessions (
                            sid		int,
                            cid		char(4),
                            sdate		date,
                            duration	int,
                            primary key (sid,cid),
                            foreign key (cid) references customers
                                on delete cascade
                        );
                    '''

    watch_query = '''
                        create table watch (
                            sid		int,
                            cid		char(4),
                            mid		int,
                            duration	int,
                            primary key (sid,cid,mid),
                            foreign key (sid,cid) references sessions,
                            foreign key (mid) references movies
                        );
                    '''

    follows_query = '''
                        create table follows (
                            cid		char(4),
                            pid		char(4),
                            primary key (cid,pid),
                            foreign key (cid) references customers,
                            foreign key (pid) references moviePeople
                        );
                    '''

    editors_query = '''
                        create table editors (
                            eid		char(4),
                            pwd		text,
                            primary key (eid)
                        );
                    '''

    cursor.execute(moviePeople_query)
    cursor.execute(movies_query)
    cursor.execute(casts_query)
    cursor.execute(recommendations_query)
    cursor.execute(customers_query)
    cursor.execute(sessions_query)
    cursor.execute(watch_query)
    cursor.execute(follows_query)
    cursor.execute(editors_query)
    connection.commit()

    return


def attemptSignIn(user, pwd):
    print(user + pwd)
    return 0


def signUpNewUser():
    path = "miniproj2.db"
    global connection, cursor
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    newUserName = input("Enter your name")
    newUserID = input("Enter your desired ID")
    newUserPassword = input("Enter desired password")
    cursor.execute("INSERT INTO CUSTOMERS VALUES (?, ?, ?)",(newUserID,newUserName,newUserPassword))
    connection.commit()



def signinscreen():
    print("1.Login\n2.Register")
    userSignInChoice = input()
    # Handle singin in
    if userSignInChoice == "1":
        # While loop to keep looping until correct user and password entered
        while True:
            signInUserName = input("Enter Id: ")
            signInPassword = input("Enter password: ")
            signInResult = attemptSignIn(signInUserName, signInPassword)
            if signInResult == 0:
                break
            else:
                print("Incorrect information, please try again! ")


if __name__ == '__main__':
    conn = sqlite3.connect('./project.db')
    connect(connection)
    drop_tables()
    define_tables()
    signinscreen()
