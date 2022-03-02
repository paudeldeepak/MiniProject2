import genericpath
import sqlite3
import os.path
from os import path
import time
import hashlib
import logging


def setupdatabase(path="miniproj2.db"):
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

<<<<<<< HEAD
<<<<<<< HEAD
def attemptSignIn(user,pwd):
    print(user+pwd)
=======
def attemptSignIn(user, pwd):
    print(user + pwd)
    return 0
>>>>>>> redemption
=======

def attemptSignIn(user, pwd):
    print(user + pwd)
    return 0

>>>>>>> 0dae82b56d202c4549e2ab19c6f5651575dc7484

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
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
=======
    # Handle singin in fixed
>>>>>>> redeption
=======
    # Handle singin in fixed
>>>>>>> redemption
=======
    # Handle singin in
>>>>>>> 0dae82b56d202c4549e2ab19c6f5651575dc7484
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
    elif userSignInChoice == "2":
        signUpNewUser()


if __name__ == '__main__':
    if (path.exists("miniproj2.db")):
        logging.info("Database already exists")
    else:
        setupdatabase()
    signinscreen()

#fixed