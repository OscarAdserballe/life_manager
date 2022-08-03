import time
import datetime
import win32gui 
import sched
from pywinauto import Application
import sqlite3
from subprocess import call
import pathlib

# connecting to database

directory_path = str(pathlib.Path().resolve())
if "Desktop" in directory_path:
    db_path = directory_path.replace("Desktop", "") + "OneDrive\Coding Projects\Life Manager\\app_database"
else:
    db_path = "app_database"

conn = sqlite3.connect(db_path)
c = conn.cursor()

#for having it run in the background
event_schedule = sched.scheduler(time.time, time.sleep)

ACTIVITIES = {
    "Coding" : ["Code.exe", "GitHub"],
    "Email" : ["mail.google.com", "outlook.office.com"], 
    "Desktop" : ["explorer.exe"], 
    "Notion" : ["Notion.exe", "notion.so"],
    "Browsing" : ["chrome.exe"],
    "YouTube" : ["YouTube"],
    "Streaming" : ["Netflix", "primevideo.com", "Prime Video", "HBO"],
    "Research" : [".pdf", "Acrobat.exe"], 
    "E-Learning" : ["coursera.org", "edx.org"], 
    "Else" : ["Unrecognizable gibberish skdjfasjd;fds"]
}

# Based on, and
# Snippets of code taken from https://github.com/KalleHallden/AutoTimer/blob/master/autotimer.py
# getting name of active window
def get_active_window():
    foreground_window = win32gui.GetForegroundWindow()
    active_window_name = win32gui.GetWindowText(foreground_window)
    link = ""
    # also link if Chrome
    # from https://stackoverflow.com/questions/52675506/get-chrome-tab-url-in-python
    if "Google Chrome" in active_window_name:
        try:
            app = Application(backend='uia')
            app.connect(title_re=".*Chrome.*")
            element_name= "Address and search bar"
            dlg = app.top_window()
            url = dlg.child_window(title=element_name, control_type="Edit").get_value()
            link = "https://" + url

        except:
            print("Did not get link")

    return active_window_name, link

# getting name of running application
import psutil, win32process, win32gui, time
def active_window_process_name():
    pid = win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow()) #This produces a list of PIDs active window relates to
    process = psutil.Process(pid[-1]).name() #pid[-1] is the most likely to survive last longer
    return process # for example, Spotify.exe

# main function that will run continuously
def background():
    # just indiscriminately catching all errors
    # to ensure it continually runs
    try:
        # initialising time
        now = datetime.datetime.now()
        formatted_date = now.strftime("%Y-%m-%d")
        formatted_time = now.strftime("%H:%M:%S")

        window_name, link = get_active_window()

        #print(window_name, link)
        window_app = active_window_process_name()

        activities = []
        for activity_name in ACTIVITIES:                                                                                                                                                                       

            for activity_identifier in ACTIVITIES[activity_name]:

                if (activity_identifier in window_name) or (activity_identifier in window_app) or (activity_identifier in link):

                    if activity_name not in activities:
                        activities.append(activity_name)
        
        prev_data_pt = c.execute("SELECT * FROM time_tracker ORDER BY date DESC, time DESC LIMIT 1;")
        prev_data_pt = prev_data_pt.fetchall()[0]

        # only if non-repeating task
        if (str(window_name), window_app, str(activities), link) != prev_data_pt[2:]:
            # inserting entry into table
            c.execute("INSERT INTO time_tracker (date, time, window_name, app, activities, link) VALUES\
                (?, ?, ?, ?, ?, ?);", (formatted_date, formatted_time, str(window_name), window_app, str(activities), link))
            conn.commit()

        # print("Row done", formatted_date, formatted_time, str(window_name), link)

        # reinserting into event schedule such that it loops continuosly. But only if there's no event
        # making sure no duplicate instances run
        # print(len(event_schedule.queue), event_schedule.queue)
        if len(event_schedule.queue) == 0:
            event_schedule.enter(5, 1, background)

        return 0
        
    except Exception as e:
        print(e)
        print("Some error occurred while using: ")
        print(len(event_schedule.queue), event_schedule.queue)
        try:
            print(formatted_time)
            print(window_app)
            print(window_name)
        except:
            print("Not even the error information could be output")
        event_schedule.enter(5, 1, background)
        return 1

    
# initialising process into schedule


event_schedule.enter(1, 1, background)
event_schedule.run()


# instructions ####
# running using pythonw time_tracker.pyw
# executing using taskkill /pid pythonw.exe /f