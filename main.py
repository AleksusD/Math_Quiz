from flask import Flask, render_template, request, redirect, url_for
import json
import sqlite3
from argon2 import PasswordHasher

app = Flask(__name__)

global connected
connected = False
global myID
global myName
global enteredUsername
global enteredPassword


def insert_sql(cmd, vals=None):
  conn = sqlite3.connect('flask.db')
  c = conn.cursor()
  res = c.execute(cmd, vals).fetchall()
  conn.commit()
  conn.close()
  return res


def select_sql(cmd):
  conn = sqlite3.connect('flask.db')
  c = conn.cursor()
  res = c.execute(cmd).fetchall()
  conn.commit()
  conn.close()
  return res


select_sql("CREATE TABLE IF NOT EXISTS User (\
           user_id INTEGER PRIMARY KEY AUTOINCREMENT, \
           username TEXT NOT NULL UNIQUE, \
           password TEXT NOT NULL)")


@app.route('/')
def home():
  if connected == True:
    return redirect("/start")
  else:
    return render_template("index.html")


@app.route('/login', methods=["GET", "POST"])
def login():
  global connected
  global myID
  global myName
  global enteredUsername
  global enteredPassword
  if request.method == "POST":
    enteredUsername = request.form["username"]
    enteredPassword = request.form["password"]

    if enteredUsername and enteredPassword:
      pwHasher = PasswordHasher()
      conn = sqlite3.connect('flask.db')
      c = conn.cursor()
      query = "SELECT password FROM User WHERE username = ?"
      hashPassword = c.execute(query, (enteredUsername, )).fetchall()
      print(type(hashPassword), hashPassword)

      hashPasswordBit = bytes(''.join(hashPassword[0]), "utf-8")
      print(type(hashPasswordBit), hashPasswordBit)
      enterPasswordBit = bytes(enteredPassword, "utf-8")
      print(type(enterPasswordBit), enterPasswordBit)

      verification = pwHasher.verify(hashPasswordBit, enterPasswordBit)

      if verification:
        connected = True
        query = "SELECT userID FROM User WHERE username = ?"
        userData = c.execute(query, (enteredUsername, )).fetchall()
        print("<><>", userData)
        myID, myName, userData[0]

        conn.commit()
        conn.close()

      return redirect("/")
    else:
      return render_template("login.html")


@app.route('/register', methods=["GET", "POST"])
def register():
  newUser = {}
  ph = PasswordHasher()

  if request.method == "POST" and request.form["username"] and request.form[
      "password"]:
    newUser["username"] = request.form["username"]
    newUser["password"] = ph.hash(bytes(request.form["password"], "utf-8"))

    insert_sql("INSERT INTO User (username, password) VALUES (?,?)",
               (newUser["username"], newUser["password"]))
  return redirect("/")


if __name__ == "__main__":
  app.run(host='0.0.0.0', port=8080)
