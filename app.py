import pandas as pd
import json
import requests
import sqlite3
import os
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, date
import helper_functions
import numpy as np
import matplotlib.pyplot as plt
from helper_functions import login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

ACTIVITIES = helper_functions.return_activities_dict()

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

now = datetime.now()
datetime_obj = now.strftime("%Y-%m-%d %H:%M:%S")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/index", methods=["GET", "POST"])
@login_required
def index():

    user_id = session["user_id"]

    conn = sqlite3.connect("app_database")
    c = conn.cursor()
    # entry with date 1900-01-01 containing days_shown in desc.
    if request.method == "POST":

        # user submitting entry into calendar
        register = request.form.get("register")
        if register:
            description = request.form.get("description")
            date = request.form.get("date")
            start = request.form.get("start")
            c.execute("INSERT INTO calendar (user_id, date, time, description) VALUES (?, ?, ?, ?);", (user_id, date, start, description))
            conn.commit()

        # user has submitted how many days should be shown
        if request.form.get("register_days") != None:
            
            days_shown = request.form.get("days_shown")
            print("Updating days shown. Now", days_shown)
            c.execute("UPDATE calendar SET description=? WHERE date=1900-01-01 AND user_id=?;", (days_shown, user_id))
            conn.commit()

    nb_days = c.execute("SELECT description FROM calendar WHERE date=1900-01-01 AND user_id=?;", (user_id, ))
    for row in nb_days:
        dates_shown = int(row[0])

    dates = helper_functions.get_days(dates_shown)

    # to check in sql, needs to be formatted specially
    sql_dates = helper_functions.get_days_sql(dates_shown)

    calendar = {}

    for i in range(dates_shown):
        calendar[dates[i]] = [False]
        calendar_entries = c.execute("SELECT * FROM calendar WHERE date=? AND user_id=?;", (sql_dates[i], user_id))
        for row in calendar_entries:
            calendar[dates[i]].append(row)
        
        # if there are actual entries, change initial value to be true
        # such that it's shown on website
        if calendar[dates[i]] != [False]:
            calendar[dates[i]][0] = True
        
        # print(dates[i], calendar[dates[i]])


    return render_template("index.html", calendar=calendar)


@app.route("/video_notes", methods=["GET", "POST"])
@login_required
def video_notes():
    user_id = session["user_id"]

    conn = sqlite3.connect("app_database")
    c = conn.cursor()

    notes = c.execute("SELECT * FROM video_notes WHERE user_id=? ORDER BY updated DESC;", (user_id, ))
    # formatting them, such that link, thumbnail etc. is extracted properly
    new_notes = helper_functions.format_video_notes(notes)
    
    # the kind of funky implemenation because ofn ote being primary key
    # in video notes, also highlights the weakness of using that as
    # a primary key
    # plus, a scenario where several users have same notes is
    # very imaginable.
    if request.method == "POST":
        if request.form.get("folder") is not None:
            # folder name which note should be added to as well as note id
            # max split 1, because inside primary key of note might be a comma
            folder_id, video_note_id = request.form.get("folder").split(", ", 1)
            print("Folder name, ", folder_id, video_note_id)
            existing_folders = c.execute("SELECT folders FROM video_notes WHERE id=?", (video_note_id, ))
            existing_folders = existing_folders.fetchall()[0][0]
            print("Existing", existing_folders)

            # inputting first folder as simple integer
            if existing_folders is None:
                print("Creating folders for note", video_note_id)

                # slight tweak here to make it recognisable in folders section of code
                set_folder_id = " " + str(folder_id) + ", "
                c.execute("UPDATE video_notes SET folders=? WHERE id=?", (set_folder_id, video_note_id))
                conn.commit()
            
            # appending folder id to list of existing ones seperated by commas
            else:
                if folder_id not in existing_folders:
                    new_folders = existing_folders + folder_id + ", "
                    c.execute("UPDATE video_notes SET folders=? WHERE id=?", (new_folders, video_note_id))
                    conn.commit()
                    print("Now, existing", new_folders)
            # folders in format, "1, 2, 3, 8"
            #existing_folders = [int(folder) for folder in existing_folders.split(",")]
            # print("existing", existing_folders)

    folder_options = c.execute("SELECT * FROM folders WHERE user_id=?", (user_id, ))
    # really weird bug if I don't iterate through it
    # and make a new folders list. Otherwise, for seom
    # weird reason, it confuses folders var with notes var???
    folders = []
    for folder in folder_options:
        folders.append(folder)

    return render_template("video_notes.html", notes=new_notes, folders=folders)

@app.route("/task_list", methods=["GET", "POST"])
@login_required
def task_list():
    user_id = session["user_id"]
    conn = sqlite3.connect("app_database")
    c = conn.cursor()

    if request.method == "POST":
        submit_task = request.form.get("submit_task")
        delete = request.form.get("delete")

        now = datetime.now()
        datetime_obj = now.strftime("%Y-%m-%d %H:%M:%S")

        if submit_task is not None:
            task_desc = request.form.get("task")
            print("Inserting", task_desc, "into task list")
            c.execute("INSERT INTO task_list (user_id, task, created, done)\
                 VALUES (?, ?, ?, 0);", (user_id, task_desc, datetime_obj))
            conn.commit()
        
        if delete is not None:
            print("Deleting", delete)
            
            c.execute("UPDATE task_list SET done=1 WHERE id=?;", (delete, ))
            conn.commit()
    
    tasks = c.execute("SELECT * FROM task_list WHERE user_id=?;", (user_id, ))

    return render_template("task_list.html", tasks=tasks)


@app.route("/notes", methods=["GET", "POST"])
@login_required
def notes():
    user_id = session["user_id"]

    conn = sqlite3.connect("app_database")
    c = conn.cursor()

    if request.method == "POST":
        submit_task = request.form.get("submit_note")
        delete = request.form.get("delete")
        
        
        
        if submit_task is not None:
            title = request.form.get("title")

            print(title)
            note = request.form.get("note")
            print("Inserting", note, "into table notes with title", title)

            now = datetime.now()
            datetime_obj = now.strftime("%Y-%m-%d %H:%M:%S")

            c.execute("INSERT INTO notes (user_id, note, title, created, hide) VALUES (?, ?, ?, ?, 0);", (user_id, note, title, datetime_obj))
            conn.commit()
        
        if delete is not None:
            c.execute("UPDATE notes SET hide=1 WHERE id=?;", (delete, ))
            conn.commit()

            
        if request.form.get("folder") is not None:
            # folder name which note should be added to as well as note id
            folder_id, note_id = request.form.get("folder").split(", ")
            print("Folder name, ", folder_id, note_id)
            existing_folders = c.execute("SELECT folders FROM notes WHERE id=?", (note_id, ))
            existing_folders = existing_folders.fetchall()[0][0]
            print("Existing", existing_folders)

            # inputting first folder as simple integer
            if existing_folders is None:
                print("Creating folders for note", note_id)
                set_folder_id = " " + str(folder_id) + ", "
                c.execute("UPDATE notes SET folders=? WHERE id=?", (set_folder_id, note_id))
                conn.commit()
            
            # appending folder id to list of existing ones seperated by commas
            else:
                if folder_id not in existing_folders:
                    new_folders = existing_folders + folder_id + ", "
                    c.execute("UPDATE notes SET folders=? WHERE id=?", (new_folders, note_id))
                    conn.commit()
                    print("Now, existing", new_folders)
            # folders in format, "1, 2, 3, 8"
            #existing_folders = [int(folder) for folder in existing_folders.split(",")]
            # print("existing", existing_folders)

    folder_options = c.execute("SELECT * FROM folders WHERE user_id=?", (user_id, ))
    # really weird bug if I don't iterate through it
    # and make a new folders list. Otherwise, for seom
    # weird reason, it confuses folders var with notes var???
    folders = []
    for folder in folder_options:
        folders.append(folder)

    notes = c.execute("SELECT * FROM notes ORDER BY created DESC;")

    return render_template("notes.html", folders=folders, notes=notes)

@app.route("/", methods=["GET", "POST"])
def redirect_user():
    return redirect("/index")

@app.route("/time_tracker", methods=["GET", "POST"])
@login_required
def time_tracker():
    user_id = session["user_id"]

    conn = sqlite3.connect("app_database")
    c = conn.cursor()

    day = "all"
    if request.method == "GET":
        day = request.args.get("date")

    
    if not day:
        day = date.today()
        day = day.strftime("%Y-%m-%d")
    
    print("Day", day)

    activity = None

    now = datetime.now()
    hour_minute = now.strftime("%H:%M")

    if request.method == "POST":
        # user submitting entry into calendar
        try:
            if request.args.get("date") is not None:
                day = request.args.get("date")
        except:
            print("Error! - Could not get date from user input")

        activity = request.form.get("category")

    db = helper_functions.get_db(day)
    
    show_db = helper_functions.get_db(day, activity)

    # Gantt chart
    helper_functions.gantt_chart(day, db, hour_minute=hour_minute)
    img_src = "static\\time_spent\\" + day + hour_minute + ".png"

    return render_template("time_tracker.html", img_src=img_src, show_db=show_db, ACTIVITIES=ACTIVITIES)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    conn = sqlite3.connect("app_database")
    c = conn.cursor()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("login.html")

        # Query database for username
        rows = c.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"), )).fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0][2], request.form.get("password")):
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0][0]

        # Redirect user to home page
        return redirect("/index")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/index")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    conn = sqlite3.connect("app_database")
    c = conn.cursor()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirmation")
        # checking for username
        if not username:
            return render_template("login.html")

        # checking for password
        elif not password:
            return render_template("login.html")

        elif not confirm_password:
            return render_template("login.html")

        elif password != confirm_password:
            return render_template("login.html")

        # user input has been validated sufficiently
        # input new user in SQL if not there already

        # checking if username is already used
        names = c.execute("SELECT username FROM users;")

        for user in names:
            if user['username'] == username:
                return render_template("register.html")
        # username not used, hence inserting it into sql database
        c.execute("INSERT INTO users (username, hash) VALUES (?, ?);", (username, generate_password_hash(password)))
        conn.commit()

        #Go to homepage following registration
        return redirect("/index")

    return render_template("register.html")

@app.route("/reading_list", methods=["GET", "POST"])
@login_required
def reading_list():
    return render_template("reading_list.html")

@app.route("/folders", methods=["GET", "POST"])
@login_required
def folders():
    user_id = session["user_id"]

    conn = sqlite3.connect("app_database")
    c = conn.cursor()
    
    # code for adding new folder to folders table
    folder_name = request.form.get("folder_name")
    if folder_name is not None:
        print("Inserting", folder_name, "into folders")
        c.execute("INSERT INTO folders (user_id, name)\
                VALUES (?, ?);", (user_id, folder_name))
        conn.commit()

    folders = []
    temp_folders = c.execute("SELECT * FROM folders WHERE user_id=? ORDER BY id DESC", (user_id, ))

    # empty dicts to store notes and video_ntoes (values)
    # associated iwth folder ids (keys)
    notes = {}
    video_notes = {}

    for i in temp_folders.fetchall():
        print("checking id, ", i[0])
        # for generating folders list
        folders.append(i)
        # getting notes and video_notes
        # folders in format " 1, 2, 4" so recognisable by that signature
        # ...except first one, so slight modification in how first one is stored
        identifier = "% " + str(i[0]) + ",%"
        notes_per_id = c.execute("SELECT * FROM notes WHERE folders LIKE ? AND user_id=? AND hide=0", (identifier, user_id))
        notes_per_id = notes_per_id.fetchall()
        if notes_per_id is not None:
            notes[i[0]] = notes_per_id
        
        
        video_notes_per_id = c.execute("SELECT * FROM video_notes WHERE folders LIKE ? AND user_id=?", (identifier, user_id))
        video_notes_per_id = helper_functions.format_video_notes(video_notes_per_id)
        if video_notes_per_id is not None:
            video_notes[i[0]] = video_notes_per_id    
    

    return render_template("folders.html", folders=folders, notes=notes, video_notes=video_notes)