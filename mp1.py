from ast import keyword
from asyncio.windows_events import NULL
import sqlite3
import random
from datetime import date
import os.path
from unittest.mock import NonCallableMagicMock
from collections import Counter

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
    
    cursor.execute("SELECT sid FROM sessions")
    row = cursor.fetchall()
    sid = random.randint(0,9999)

    new_sid_list = []

    if (row != NULL):
        for i in range(0, len(row)):
            new_sid_list.append(row[i][0])

    while sid in new_sid_list:
        sid = random.randint(0,1000)

    sdate = date.today()

    duration = NULL
    cursor.execute("INSERT INTO sessions VALUES (?, ?, ?, ?)",(sid,cid,sdate,duration))
    connection.commit()
    return 

def searchMovies():
    global connection, cursor

    keyw = input("Enter a keyword or multiple keywords seperated by a comma to begin searching for a movie: ")
    print()
    keyw = keyw.lower()
    keywords_list = list(keyw.split(","))
    for i in range(0, len(keywords_list)):
        keywords_list[i] = keywords_list[i].strip()

    movie_list = []

    for keywords in keywords_list:
        cursor.execute('''SELECT m.title, m.year, m.runtime, group_concat(DISTINCT c.role)
                          FROM movies m, casts c 
                          WHERE m.mid = c.mid 
                          AND LOWER(m.title) LIKE ?
                          GROUP BY m.title''', ('%'+keywords+'%' ,))
        q1 = cursor.fetchall()
        if q1[0][0] != None:
            movie_list.extend(q1)
        cursor.execute('''SELECT m.title, m.year, m.runtime, group_concat(DISTINCT c2.role)
                          FROM movies m, casts c1, casts c2 
                          WHERE m.mid = c1.mid 
                          AND m.mid = c2.mid
                          AND LOWER(c1.role) LIKE ?
                          GROUP BY m.title''', ('%'+keywords+'%' ,))
        q2 = cursor.fetchall()
        if q2[0][0] != None:
            movie_list.extend(q2)
        cursor.execute('''SELECT m.title, m.year, m.runtime, group_concat(DISTINCT c2.role) 
                          FROM movies m, casts c1, casts c2, moviePeople p 
                          WHERE m.mid = c1.mid
                          AND m.mid = c2.mid 
                          AND c1.pid = p.pid 
                          AND LOWER(p.name) LIKE ?
                          GROUP BY m.title''', ('%'+keywords+'%' ,))
        q3 = cursor.fetchall()
        if q3[0][0] != None:
            movie_list.extend(q3)
    
    print(movie_list)
    movie_counter = (Counter(movie_list))

    print(movie_counter)

    count = 0
    threshold = 5
    choice = ''
    while choice != '-':
        for movies in movie_counter:
            if count == threshold:
                if len(movie_counter) > threshold:
                    print("\nTo see more matches type '+'.", end = ' ')
                break
            elif (count < threshold and count > (threshold-6)) :
                print(str(count+1) + ".", movies[0],"  Year:",movies[1],"  Duration:",str(movies[2])+" minutes")
            count += 1
        choice = input("\nTo exit type '-'. Otherwise type the number besides the movie to see more information: ")
        if choice == '+':
            count = 0
            threshold += 5
            print()
        elif (int(choice) > 0 and int(choice) <= len(movie_counter)):
            print('CHOSEN MOVIE IS:', list(movie_counter.keys())[0][0])

def onExit():
    global connection, cursor

    connection.commit()
    connection.close()

def main():
    
    path = './miniproj2.db'
    connect(path)

    if(not os.path.exists('./miniproj2.db')):
        drop_tables()
        define_tables()

    #signinscreen()
    #(id,roleToAccess) = signinscreen()
    # RoleToAcess: 1 = customer , 2=editors, 0 = error
    id = 'c100'
    roleToAccess = 1
    if(roleToAccess == 1):
        #startSession(id)
        searchMovies()
    elif(roleToAccess == 2):
        # do somethiong
        # place holder v
        startSession(id)
    
    onExit()

main()