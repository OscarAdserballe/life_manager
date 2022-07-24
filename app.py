import pandas as pd
import json
import requests
import sqlite3
import os
from flask import Flask, flash, redirect, render_template, request, session
from datetime import datetime, date
import helper_functions
import numpy as np
import matplotlib.pyplot as plt
import ast


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

#data fields stored
COLUMN_NAMES = ["thumbnail", "title", "summary_html_format", "updated_at", "created_at", "id", "notes"]

ACTIVITIES = helper_functions.return_activities_dict()

now = datetime.now()
datetime_obj = now.strftime("%Y-%m-%d %H:%M:%S")

@app.route("/", methods=["GET", "POST"])
def index():
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
            c.execute("INSERT INTO calendar (date, time, description) VALUES (?, ?, ?);", (date, start, description))
            conn.commit()

        # user has submitted how many days anew
        register_days = request.form.get("register_days")
        if register_days != None:
            days_shown = request.form.get("days_shown")
            c.execute("UPDATE calendar SET description = ? WHERE date=1900-01-01;", (days_shown, ))
            conn.commit()

    nb_days = c.execute("SELECT description FROM calendar WHERE date=1900-01-01;")
    for row in nb_days:
        dates_shown = int(row[0])

    dates = helper_functions.get_days(dates_shown)

    # to check in sql, needs to be formatted specially
    sql_dates = helper_functions.get_days_sql(dates_shown)

    calendar = {}

    for i in range(dates_shown):
        calendar[dates[i]] = [False]
        calendar_entries = c.execute("SELECT * FROM calendar WHERE date=?;", (sql_dates[i],))
        for row in calendar_entries:
            calendar[dates[i]].append(row)
        
        # if there are actual entries, change initial value to be true
        # such that it's shown on website
        if calendar[dates[i]] != [False]:
            calendar[dates[i]][0] = True
        
        # print(dates[i], calendar[dates[i]])


    return render_template("index.html", calendar=calendar)


@app.route("/video_notes", methods=["GET", "POST"])
def video_notes():
    conn = sqlite3.connect("app_database")
    c = conn.cursor()

    notes = c.execute("SELECT * FROM video_notes ORDER BY updated_at DESC;")
    conn.commit()
    new_notes = []
    for row in notes:
        intermediary_list = []
        for j in range(len(row)):
            # only image links, but they have video id
            # https://www.youtube.com/watch?v={{ video_id }}
            # and https://i.ytimg.com/vi/eHYpcXWCkUM/mqdefault.jpg
            try:
                if j == 0:
                    link = row[j].split("/")
                    yt_link = "https://www.youtube.com/watch?v=" + link[4]
                    to_append = [row[j], yt_link]
                    intermediary_list.append(to_append)
                elif j == 6:
                    # convert string representation of dict to dict
                    intermediary_list.append(ast.literal_eval(row[j]))
                else:
                    intermediary_list.append(row[j])
                # print(intermediary_list)
            except:
                pass
        new_notes.append(intermediary_list)
            


    return render_template("video_notes.html", notes=new_notes)

@app.route("/task_list", methods=["GET", "POST"])
def task_list():
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
            id_container = c.execute("SELECT COUNT(*) FROM task_list;")
            for row in id_container:
                id = row[0] + 1

            

            c.execute("INSERT INTO task_list (id, task, time_created, done) VALUES (?, ?, ?, 0);", (id, task_desc, datetime_obj))
            conn.commit()
        
        if delete is not None:
            print("Deleting", delete)
            
            c.execute("UPDATE task_list SET time_deleted=?, done=1 WHERE id=?;", (datetime_obj, delete))
            conn.commit()
    
    tasks = c.execute("SELECT * FROM task_list;")
    conn.commit()

    return render_template("task_list.html", tasks=tasks)


@app.route("/notes", methods=["GET", "POST"])
def notes():
    conn = sqlite3.connect("app_database")
    c = conn.cursor()

    if request.method == "POST":
        submit_task = request.form.get("submit_note")

        if submit_task is not None:
            note = request.form.get("note")
            print("Inserting", note, "into table notes")
            id_container = c.execute("SELECT COUNT(*) FROM notes;")
            for row in id_container:
                id = row[0] + 1

            now = datetime.now()
            datetime_obj = now.strftime("%Y-%m-%d %H:%M:%S")

            c.execute("INSERT INTO notes (id, note, time_created) VALUES (?, ?, ?);", (id, note, datetime_obj))
            conn.commit()

    notes = c.execute("SELECT * FROM notes ORDER BY time_created DESC;")
    conn.commit()

    return render_template("notes.html", notes=notes)

@app.route("/time_tracker", methods=["GET", "POST"])
def time_tracker():

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
        if request.args.get("date") is not None:
            day = request.args.get("date")

        activity = request.form.get("category")

    db = helper_functions.get_db(day)
    
    show_db = helper_functions.get_db(day, activity)

    # Gantt chart
    helper_functions.gantt_chart(day, helper_functions.classify_data(db), hour_minute=hour_minute)
    img_src = "static\\time_spent\\" + day + hour_minute + ".png"

    return render_template("time_tracker.html", img_src=img_src, show_db=show_db, ACTIVITIES=ACTIVITIES)




