import genericpath
import sqlite3
import os.path
from os import path
import time
import hashlib
import logging

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
    # Handle singin in fixed
    if userSignInChoice == "1":
        #While loop to keep looping until correct user and password entered
        while(True):
            signInUserName  = input("Enter Id: ")
            signInPassword = input("Enter password: ")
            signInResult = attemptSignIn(signInUserName,signInPassword)
            if(signInResult == 0):
                break
            else:
                print("Incorrect information, please try again! ")


if __name__ == '__main__':
    conn = sqlite3.connect('./project.db')
    connect(path)
    signinscreen()

#fixed