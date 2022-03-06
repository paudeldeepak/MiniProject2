from ast import keyword
from asyncio.windows_events import NULL
import sqlite3
import random
from datetime import date
import os.path
from tkinter import E
from unittest.mock import NonCallableMagicMock
from collections import Counter
from getpass import getpass

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
    print("\n##### STARTUP MENU #####")
    print("1. Login\n2. Register")
    print("\nType the number besides the option to select. Type '-' to exit.")
    userSignInChoice = input("Enter your selection: ")

    # Handle singin in
    if userSignInChoice == "1":
        # While loop to keep looping until correct user and password entered
        while True:
            print("\n##### LOGIN MENU #####")
            signInUserName = input("Enter Id: ")
            signInPassword = getpass("Enter password: ")
            signInResult = attemptSignIn(signInUserName, signInPassword)
            # Return 1 = customer , 2=editors, 0 = error
            if signInResult == 1:
                return (signInUserName,1)
            elif signInResult == 2:
                return (signInUserName,2)
            elif signInResult == 0:
                print("\n*Incorrect information, please try again!*")
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

    print("\n##### REGISTRATION MENU #####")
    newUserName = input("Enter your name: ")
    newUserID = input("Enter your desired ID: ")
    newUserPassword = input("Enter desired password: ")
    cursor.execute("INSERT INTO customers VALUES (?, ?, ?)",(newUserID,newUserName,newUserPassword))
    connection.commit()
    return newUserID

def startSession(cid):
    global connection, cursor
    
    print('\n##### SESSION CREATION MENU #####')
    print('1. Create new session')
    print("\nType the number besides the option to select. Type '-' to return to the main menu.")
    ses_crt_menu = input("Enter your selection: ")

    if ses_crt_menu == '-':
        return

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

    print('\nSession successfully created')

    return sid

def searchMovies(cid, sid):
    global connection, cursor

    keyw = input("Enter a keyword or multiple keywords seperated by a comma to begin searching for a movie: ")
    print()
    keyw = keyw.lower()
    keywords_list = list(keyw.split(","))
    for i in range(0, len(keywords_list)):
        keywords_list[i] = keywords_list[i].strip()

    movie_list = []

    for keywords in keywords_list:
        cursor.execute('''SELECT m.title, m.year, m.runtime, group_concat(DISTINCT c.role), group_concat(DISTINCT c.pid), s.watch_count, m.mid
                          FROM movies m, casts c JOIN (SELECT w.mid as movid, COUNT(DISTINCT w.cid) as watch_count
                          FROM movies m, watch w
                          WHERE m.mid = w.mid
                          AND w.duration*100/m.runtime > 49
                          GROUP BY w.mid) s ON m.mid = s.movid
                          WHERE m.mid = c.mid 
                          AND LOWER(m.title) LIKE ?
                          GROUP BY m.title''', ('%'+keywords+'%' ,))
        movie_list.extend(cursor.fetchall())

        cursor.execute('''SELECT m.title, m.year, m.runtime, group_concat(DISTINCT c2.role), group_concat(DISTINCT c2.pid), s.watch_count, m.mid
                          FROM movies m, casts c1, casts c2 JOIN (SELECT w.mid as movid, COUNT(DISTINCT w.cid) as watch_count
                          FROM movies m, watch w
                          WHERE m.mid = w.mid
                          AND w.duration*100/m.runtime > 49
                          GROUP BY w.mid) s ON m.mid = s.movid
                          WHERE m.mid = c1.mid 
                          AND m.mid = c2.mid
                          AND LOWER(c1.role) LIKE ?
                          GROUP BY m.title''', ('%'+keywords+'%' ,))
        movie_list.extend(cursor.fetchall())

        cursor.execute('''SELECT m.title, m.year, m.runtime, group_concat(DISTINCT c2.role), group_concat(DISTINCT c2.pid), s.watch_count, m.mid
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
        movie_list.extend(cursor.fetchall())
    
    print(movie_list)
    movie_counter = (Counter(movie_list))

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
        elif choice != '-' and int(choice) > 0 and int(choice) <= len(movie_counter):
            follow_choice = ''

            while follow_choice != '-':
                int_choice = int(choice) - 1
                movie_name = list(movie_counter.keys())[int_choice][0]
                movie_mid = list(movie_counter.keys())[int_choice][6]
                cast_list = list((list(movie_counter.keys())[int_choice][3]).split(","))
                cast_pid_list = list((list(movie_counter.keys())[int_choice][4]).split(","))

                print('\n'+movie_name+'\nCast:')
                for cast_ind in range(0,len(cast_list)):
                    print(str(cast_ind+1)+'.',cast_list[cast_ind])
                print('# of customers who have viewed:', list(movie_counter.keys())[int_choice][5])

                print("To go back type '-'.") 
                follow_choice = input("To start watching the movie type '0' Otherwise type the number besides the cast member to follow them: ")

                if follow_choice.isdigit and follow_choice != '-':
                    if int(follow_choice) == 0:
                        try:
                            cursor.execute("INSERT INTO watch VALUES (?, ?, ?, ?)",(sid, cid, movie_mid, 0))
                            connection.commit()
                            print('\nYou are now watching', movie_name)
                        except:
                            print('\nYou are already watching', movie_name)

                    elif int(follow_choice) > 0 and int(follow_choice) <= len(cast_list):
                        try:
                            cursor.execute("INSERT INTO follows VALUES (?, ?)",(cid, cast_pid_list[int(follow_choice)-1]))
                            connection.commit()
                            print('\nYou are now following', cast_list[int(follow_choice)-1], cast_pid_list[int(follow_choice)-1])
                        except:
                            print('\nYou are already following', cast_list[int(follow_choice)-1])
                else:
                    print("That's not an int!")

        elif (choice == '-'):
            break
    connection.commit()

def watching_movie_list(cid, sid):
    global connection, cursor

    cursor.execute('''SELECT m.title, m.mid, m.runtime
                      FROM movies m, watch w
                      WHERE m.mid = w.mid
                      AND w.cid = ?
                      AND w.sid = ?
                      AND w.duration = 0
                   ''', (cid, sid))
    connection.commit()

    return cursor.fetchall()

def end_this_movie(duration, runtime, cid, sid, mid):
    global connection, cursor

    if duration > runtime:
        duration = runtime

    cursor.execute('''UPDATE watch
                      SET duration = ?
                      WHERE cid = ?
                      AND sid = ?
                      AND mid = ?
                      AND duration = 0
                   ''', (duration, cid, sid, mid))
    connection.commit()

    return

def end_movie(cid, sid):
    global connection, cursor

    duration = 200

    movie_list = watching_movie_list(cid, sid)

    print('\n##### MOVIE MENU #####')
    for movie_ind in range(0, len(movie_list)):
        print(str(movie_ind+1)+'.',movie_list[movie_ind][0])
    
    if len(movie_list) == 0:
        print('*You are not watching any movies*')

    print("\nType '-' to return to the main menu")
    movie_menu = input("Enter the number of the movie you'd like to stop watching: ")

    if movie_menu == '-':
        return
    else:
        movie_menu = int(movie_menu)-1

    end_this_movie(duration, movie_list[movie_menu][2], cid, sid, movie_list[movie_menu][1])

    print('\nYou are no longer watching', movie_list[movie_menu][0])
    
    return

def end_session(cid, sid):
    global connection, cursor

    movie_list = watching_movie_list(cid, sid)

    print('\n##### SESSION DELETION MENU #####')
    print('1. Delete current session')
    print("\nType '-' to return to the main menu. Type the number besides the option to select")
    ses_dlt_menu = input("Enter your selection: ")

    if ses_dlt_menu == '-':
        return

    duration = 69
    
    for movie_ind in range(0, len(movie_list)):
        print('Deleting:',movie_list[movie_ind][0])
        end_this_movie(duration, movie_list[movie_ind][2], cid, sid, movie_list[movie_ind][1])

    cursor.execute('''UPDATE sessions
                      SET duration = ?
                      WHERE cid = ?
                      AND sid = ?
                      AND duration = 0
                   ''', (duration, cid, sid))
    connection.commit()

    print('\nThe session has been successfully deleted')
    
    return


def onExit():
    global connection, cursor

    connection.commit()
    connection.close()
    print("Goodbye!")

def main():
    
    path = './miniproj2.db'
    databaseFile = './prj-tables.sql'

    if(not os.path.exists('./miniproj2.db')):
        connect(path)
        setupDB(databaseFile)
    else:
        connect(path)

    (id,roleToAccess) = signinscreen()
    # RoleToAcess: 1 = customer , 2=editors, 0 = error

    if(roleToAccess == 1):
        main_menu = ''
        while main_menu != '-':
            print("\n##### MAIN MENU #####")
            print("1. Start a session\n2. Search for a movie\n3. End movie viewing\n4. End session")
            print("\nType '-' to exit")
            main_menu = input("Enter the number of the menu you'd like to access: ")
            if main_menu == '1':
                sid = startSession(id)
            elif main_menu == '2':
                if sid != 0:
                    searchMovies(id, sid)
                else:
                    print('You must begin a session before searching for a movie.')
            elif main_menu == '3':
                end_movie(id, sid)
            elif main_menu == '4':
                end_session(id, sid)

    elif(roleToAccess == 2):
        # do somethiong
        # place holder v
        startSession(id)
    
    onExit()

main()
