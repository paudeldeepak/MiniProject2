from asyncio.windows_events import NULL
import sqlite3
import random
from datetime import date
import os.path
from unittest.mock import NonCallableMagicMock

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
            # Return 1 = customer , 2=editors, 0 = error
            if signInResult == 1:
                return (signInUserName,1)
            elif signInResult == 2:
                return (signInUserName,2)
            elif signInResult == 0:
                print("Incorrect information, please try again! ")
    elif userSignInChoice == "2":
        return (signUpNewUser(),1)

def attemptSignIn(user, pwd):
    global connection, cursor
    # Check if user exists in customers
    cursor.execute("SELECT name from customers WHERE cid=? AND pwd = ?;",(user,pwd))
    exist = cursor.fetchone()
    if exist is not None:
        return 1
    # Check if user exists in editors
    cursor.execute("SELECT eid from editors WHERE eid=? AND pwd = ?;",(user,pwd))
    exist = cursor.fetchone()
    if exist is not None:
        return 2
    
    return 0

def signUpNewUser():
    global connection, cursor
    newUserName = input("Enter your name: ")
    newUserID = input("Enter your desired ID: ")
    newUserPassword = input("Enter desired password: ")
    cursor.execute("INSERT INTO customers VALUES (?, ?, ?)",(newUserID,newUserName,newUserPassword))
    connection.commit()
    return newUserID

def startSession(cid):
    global connection, cursor
    print("running")
    cursor.execute("SELECT sid FROM sessions")
    row=cursor.fetchall()
    
    sid = random.randint(0,9999)

    if (row != NULL):
        while sid in row:
            sid = random.randint(0,9999)

    sdate = date.today()

    duration = NULL
    cursor.execute("INSERT INTO sessions VALUES (?, ?, ?, ?)",(sid,cid,sdate,duration))
    connection.commit()
    return 


def main():
    
    path = './miniproj2.db'
    connect(path)

    if(not os.path.exists('./miniproj2.db')):
        drop_tables()
        define_tables()

     # RoleToAcess: 1 = customer , 2=editors, 0 = error
    (id,roleToAccess) = signinscreen()
    startSession(id)
   
    

main()