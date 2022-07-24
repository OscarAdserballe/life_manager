import time
import datetime
import win32gui 
import sched
from pywinauto import Application
import sqlite3
from subprocess import call

# connecting to database
conn = sqlite3.connect("app_database")
c = conn.cursor()

#for having it run in the background
event_schedule = sched.scheduler(time.time, time.sleep)

ACTIVITES = {
    "Coding" : [["Code.exe"], False],
    "Email" : [["mail.google.com", "outlook.office.com"], False],
    "Desktop" : [["explorer.exe"], False],
    "Notion" : [["Notion.exe"], False],
    "Browsing" : [["chrome.exe"], False],
    "Youtube" : [["youtube.com"], False],
    "Netflix" : [["Netflix"], False],
    "Research" : [[".pdf"], False]
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
            element_name="Address and search bar"
            dlg = app.top_window()
            url = dlg.child_window(title=element_name, control_type="Edit").get_value()
            link = "https://" + url

            # returning link too, in case of chrome
            # it's just nice with more info on one's web browsing
            return active_window_name, link
        except:
            pass

    return active_window_name, link

# getting name of running application
import psutil, win32process, win32gui, time
def active_window_process_name():
    pid = win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow()) #This produces a list of PIDs active window relates to
    process = psutil.Process(pid[-1]).name() #pid[-1] is the most likely to survive last longer
    return process #for example, Spotify.exe

# main function that will run continuously

def background():
    # just indiscriminately catching all errors
    # to ensure it continually runs
    try:
        # initialising time
        now = datetime.datetime.now()
        formatted_date = now.strftime("%Y-%m-%d")
        formatted_time = now.strftime("%H:%M:%S")

        window = get_active_window()

        # has both window name and link
        window_name, link = window
        window_app = active_window_process_name()

        activities = []
        for activity_name in ACTIVITES:
            for activity_identifier in ACTIVITES[activity_name][0]:
                if (activity_identifier in window_name) or (activity_identifier in window_app) or (activity_identifier in link):
                    activities.append(activity_name)
        
        # inserting entry into table
        c.execute("INSERT INTO time_tracker (date, time, window_name, app, activities, link) VALUES\
            (?, ?, ?, ?, ?, ?);", (formatted_date, formatted_time, str(window_name), window_app, str(activities), link))
        conn.commit()
        # print("Row done", formatted_date, formatted_time, str(window_name), link)

        # reinserting into event schedule such that it loops continuosly. But only if there's no event
        # making sure no duplicate instances run
        # print(len(event_schedule.queue), event_schedule.queue)
        if len(event_schedule.queue) == 0:
            event_schedule.enter(10, 1, background)

        return 0
        
    except:
        print("Some error occurred")
        print(len(event_schedule.queue), event_schedule.queue)
        try:#
            print(formatted_time)
            print(window_app)
            print(window_name)
        except:
            pass
        event_schedule.enter(10, 1, background)
        return 1

    
# initialising process into schedule


event_schedule.enter(10, 1, background)
event_schedule.run()


# instructions ####
# running using pythonw time_tracker.pyw
# executing using taskkill /pid pythonw.exe /f