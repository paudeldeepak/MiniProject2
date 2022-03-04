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

def setupDB(databaseFile):
    global connection, cursor
    
    with open(databaseFile) as fp:
        cursor.executescript(fp.read())
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
        cursor.execute('''SELECT m.title, m.year, m.runtime, group_concat(DISTINCT c.role), s.watch_count
                          FROM movies m, casts c JOIN (SELECT w.mid as movid, COUNT(DISTINCT w.cid) as watch_count
                          FROM movies m, watch w
                          WHERE m.mid = w.mid
                          AND w.duration*100/m.runtime > 49
                          GROUP BY w.mid) s ON m.mid = s.movid
                          WHERE m.mid = c.mid 
                          AND LOWER(m.title) LIKE ?
                          GROUP BY m.title''', ('%'+keywords+'%' ,))
        q1 = cursor.fetchall()
        if q1[0][0] != None:
            movie_list.extend(q1)
        cursor.execute('''SELECT m.title, m.year, m.runtime, group_concat(DISTINCT c2.role), s.watch_count
                          FROM movies m, casts c1, casts c2 JOIN (SELECT w.mid as movid, COUNT(DISTINCT w.cid) as watch_count
                          FROM movies m, watch w
                          WHERE m.mid = w.mid
                          AND w.duration*100/m.runtime > 49
                          GROUP BY w.mid) s ON m.mid = s.movid
                          WHERE m.mid = c1.mid 
                          AND m.mid = c2.mid
                          AND LOWER(c1.role) LIKE ?
                          GROUP BY m.title''', ('%'+keywords+'%' ,))
        q2 = cursor.fetchall()
        if q2[0][0] != None:
            movie_list.extend(q2)
        cursor.execute('''SELECT m.title, m.year, m.runtime, group_concat(DISTINCT c2.role), s.watch_count
                          FROM movies m, casts c1, casts c2, moviePeople p JOIN (SELECT w.mid as movid, COUNT(DISTINCT w.cid) as watch_count
                          FROM movies m, watch w
                          WHERE m.mid = w.mid
                          AND w.duration*100/m.runtime > 49
                          GROUP BY w.mid) s ON m.mid = s.movid
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
            int_choice = int(choice) - 1
            print('\n'+list(movie_counter.keys())[int_choice][0]+'. Cast:', list(movie_counter.keys())[int_choice][3],' Cast:', list(movie_counter.keys())[int_choice][4])
        elif (choice == '-'):
            break

def onExit():
    global connection, cursor

    connection.commit()
    connection.close()

def main():
    
    path = './miniproj2.db'
    databaseFile = './prj-tables.sql'

    if(not os.path.exists('./miniproj2.db')):
        connect(path)
        setupDB(databaseFile)
    else:
        connect(path)

    signinscreen()
    (id,roleToAccess) = signinscreen()
    # RoleToAcess: 1 = customer , 2=editors, 0 = error
    
    if(roleToAccess == 1):
        startSession(id)
        searchMovies()
    elif(roleToAccess == 2):
        # do somethiong
        # place holder v
        startSession(id)
    
    onExit()

main()