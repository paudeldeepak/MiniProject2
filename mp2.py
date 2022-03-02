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
    with open('prj-tables.sql') as fp:
        cursor.executescript(fp.read())
    connection.commit()
    return connection, cursor

def attemptSignIn(user,pwd):
    print(user+pwd)

def signinscreen():
    print("1.Login\n2.Register")
    userSignInChoice = input()
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
