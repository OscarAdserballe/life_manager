import pandas as pd
import json
import requests
import sqlite3
import os
from flask import Flask, flash, redirect, render_template, request, session
from datetime import datetime, date, timedelta
import numpy as np
import matplotlib.pyplot as plt
import time
import calendar
import matplotlib as mpl
import socket

# implementing similarity metric
from difflib import SequenceMatcher




def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

# creating table that will store time entries
# from time_tracker.pyw
# remember to update desktop version of time_tracker.pyw
ACTIVITES = {
    "Coding" : [["Code.exe"], False],
    "Email" : [["mail.google.com", "outlook.office.com"], False],
    "Desktop" : [["explorer.exe"], False],
    "Notion" : [["Notion.exe"], False],
    "Browsing" : [["chrome.exe"], False],
    "YouTube" : [["YouTube"], False],
    "Netflix" : [["Netflix"], False],
    "Research" : [[".pdf"], False]
}

# quick way to transport activities dict to other files that need it, though doesn't
# work with time_tracker.pyw
def return_activities_dict():
    return ACTIVITES

conn = sqlite3.connect("app_database")
c = conn.cursor()

TIME_TRACKER_COLUMNS = ["date", "time", "window_name", "app", "activities", "link"]

# create time_tracker table
def create_db():
    # event characterised by id, date, time_started, window_name, link (if chrome)
    c.execute("CREATE TABLE IF NOT EXISTS time_tracker (date DATE NOT NULL,\
            time TIME NOT NULL, window_name TEXT NOT NULL, app TEXT, activities TEXT, link TEXT);")
    conn.commit()
    return 0

# create calendar table
def create_calendar_db():
    c.execute("CREATE TABLE IF NOT EXISTS calendar (date DATE NOT NULL,\
            time TIME NOT NULL, description TEXT NOT NULL);")
    conn.commit()
    return 0

# create video_notes table
def create_yt_db():
    c.execute("CREATE TABLE IF NOT EXISTS video_notes (thumbnail TEXT, title TEXT, \
            summary_html_format TEXT, updated_at TEXT, created_at TEXT, id INTEGER, notes TEXT PRIMARY KEY);")
    conn.commit()
    return 0

def create_task_list_db():
    c.execute("CREATE TABLE IF NOT EXISTS task_list (id INTEGER AUTO_INCREMENT, task TEXT NOT NULL, time_created DATETIME, time_deleted DATETIME, done INTEGER, deadline DATETIME);")
    conn.commit()
    return 0

def create_notes_db():
    c.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER AUTO_INCREMENT, note TEXT NOT NULL, time_created DATETIME);")
    conn.commit()
    return 0


# update video_notes table
def update_db():
    # using curlconverter.com ######################################
    # and copying "notes" from Network tab in dvp tools in Chrome as cURL (bash)
    # inputting it into curlconverter.com
    # different for laptop and desktop, "bertha"
    sys_name = socket.gethostname()
    if sys_name == "bertha":
        cookies = {
            '_ga': 'GA1.1.207427668.1658277351',
            'ai_user': 'IMr1HMCa0NJHSh3GyPAeZx|2022-07-20T00:35:51.486Z',
            '_hjSessionUser_1930158': 'eyJpZCI6IjA5OGI3OTNiLTY1NzItNWIyOS05MWQxLTdjMWE1MzAxMTNhYyIsImNyZWF0ZWQiOjE2NTgyNzczNTIxMDksImV4aXN0aW5nIjp0cnVlfQ==',
            'remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d': 'eyJpdiI6IjM5b25vcTBkWWlteU9hRGdXSkJPN0E9PSIsInZhbHVlIjoiaFRPTVFRRXhheExKUXZNT2VaM0YrTDhOOXN5dWt4Q0NDZzNENnlaVU14U2M2ZDF6a0lwK1FGaHdXZE04dTR4VzFNWktQb0xibXNtbFV1cHJrb2dtMXh1XC8xWU9tUmc1MTdGK1k2amNpY3dTUW5udmhMYmZtVnVsa0VtMmE3RzViYWtXcjNZQVJLZUEzQTB0UCtcL1dDUlZlUmlLWlwvclhKYXN3WitWZVFpNTJHR3BCcUo3MG02NTdFQkQxSWhsXC9HNlpIYWFraTJJaXk2bmxiU251OWdqMXZ2Y1pnUTk1azNoeGY4V0MrZjNsVmM9IiwibWFjIjoiZjg0MDZhNTIyNGQwZWU5ZThkYmNhMmQyODdiMzJjMzRiOGQyNDY2ZTZmNWQyNzgwZTcxOGMzOWU4YzUwZDRiOSJ9',
            '_hjSession_1930158': 'eyJpZCI6ImMxNzdkYjhkLWZkOGMtNDRlOS05ODQ5LTAwYzEzZGEwNTBmNSIsImNyZWF0ZWQiOjE2NTgzMDUxMzI3OTgsImluU2FtcGxlIjpmYWxzZX0=',
            'XSRF-TOKEN': 'eyJpdiI6InNWWHA5NzJEeDlxOVNtK2YrOGx2dmc9PSIsInZhbHVlIjoiSHR4V1JtNTRcL0FDYzNJNnR5Z1NGWVlxMFRCd3JjUDkyUTBoNFpscVJxUDlaUCtFVzFBTXhYMWUrZVEwZnBEYkJYNklGWHNkQllld3NKTEJtS1FNWEZRTWxYbXUxZ1JVd3ExazloS0xaMnBhWVRZYis1REgrXC9DUFN2MVdzZU9LTSIsIm1hYyI6IjI1ZDUzMDJkODRhNDVhNjdkYjA2OTk3YzliY2RkZDcyYjNkNGY2ZDU0ZGYyMWM4ZjAyNDZhYTM3NjZjMDMwZmIifQ%3D%3D',
            'tuberslab_session': 'eyJpdiI6Ijh1RzRCRUFVZFwva1NDYlV5ZXZSVzJ3PT0iLCJ2YWx1ZSI6Imp3TmhSMXhHbStqVzZIWkhobHlkSDZvQXlXYXNxeXhiQTZSaGpoSXlPXC9HaWNVcWZjRG03clc1YlExZEErc3lmYkxUQUhNaTBBY0hpNnhEcGhST21iUExRc0Q1QXZ0U1djdUxDV1YxMGRMTEpMQitkWXNCVWtnY0xcL3JINHNIdXQiLCJtYWMiOiI2OTc3ZDQ2ZWY5ZTliYzZlNGIwN2Y4NDgxMmJiMDg0YTVlODRhODdjZDdhYTNlMmE1MGRhY2JmNzVmYzFjYjRjIn0%3D',
            '_ga_FFYVNFBC5R': 'GS1.1.1658305132.2.1.1658306702.0',
        }

        headers = {
            'authority': 'www.tuberslab.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9,fr-FR;q=0.8,fr;q=0.7,da;q=0.6',
            # Requests sorts cookies= alphabetically
            # 'cookie': '_ga=GA1.1.207427668.1658277351; ai_user=IMr1HMCa0NJHSh3GyPAeZx|2022-07-20T00:35:51.486Z; _hjSessionUser_1930158=eyJpZCI6IjA5OGI3OTNiLTY1NzItNWIyOS05MWQxLTdjMWE1MzAxMTNhYyIsImNyZWF0ZWQiOjE2NTgyNzczNTIxMDksImV4aXN0aW5nIjp0cnVlfQ==; remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d=eyJpdiI6IjM5b25vcTBkWWlteU9hRGdXSkJPN0E9PSIsInZhbHVlIjoiaFRPTVFRRXhheExKUXZNT2VaM0YrTDhOOXN5dWt4Q0NDZzNENnlaVU14U2M2ZDF6a0lwK1FGaHdXZE04dTR4VzFNWktQb0xibXNtbFV1cHJrb2dtMXh1XC8xWU9tUmc1MTdGK1k2amNpY3dTUW5udmhMYmZtVnVsa0VtMmE3RzViYWtXcjNZQVJLZUEzQTB0UCtcL1dDUlZlUmlLWlwvclhKYXN3WitWZVFpNTJHR3BCcUo3MG02NTdFQkQxSWhsXC9HNlpIYWFraTJJaXk2bmxiU251OWdqMXZ2Y1pnUTk1azNoeGY4V0MrZjNsVmM9IiwibWFjIjoiZjg0MDZhNTIyNGQwZWU5ZThkYmNhMmQyODdiMzJjMzRiOGQyNDY2ZTZmNWQyNzgwZTcxOGMzOWU4YzUwZDRiOSJ9; _hjSession_1930158=eyJpZCI6ImMxNzdkYjhkLWZkOGMtNDRlOS05ODQ5LTAwYzEzZGEwNTBmNSIsImNyZWF0ZWQiOjE2NTgzMDUxMzI3OTgsImluU2FtcGxlIjpmYWxzZX0=; XSRF-TOKEN=eyJpdiI6InNWWHA5NzJEeDlxOVNtK2YrOGx2dmc9PSIsInZhbHVlIjoiSHR4V1JtNTRcL0FDYzNJNnR5Z1NGWVlxMFRCd3JjUDkyUTBoNFpscVJxUDlaUCtFVzFBTXhYMWUrZVEwZnBEYkJYNklGWHNkQllld3NKTEJtS1FNWEZRTWxYbXUxZ1JVd3ExazloS0xaMnBhWVRZYis1REgrXC9DUFN2MVdzZU9LTSIsIm1hYyI6IjI1ZDUzMDJkODRhNDVhNjdkYjA2OTk3YzliY2RkZDcyYjNkNGY2ZDU0ZGYyMWM4ZjAyNDZhYTM3NjZjMDMwZmIifQ%3D%3D; tuberslab_session=eyJpdiI6Ijh1RzRCRUFVZFwva1NDYlV5ZXZSVzJ3PT0iLCJ2YWx1ZSI6Imp3TmhSMXhHbStqVzZIWkhobHlkSDZvQXlXYXNxeXhiQTZSaGpoSXlPXC9HaWNVcWZjRG03clc1YlExZEErc3lmYkxUQUhNaTBBY0hpNnhEcGhST21iUExRc0Q1QXZ0U1djdUxDV1YxMGRMTEpMQitkWXNCVWtnY0xcL3JINHNIdXQiLCJtYWMiOiI2OTc3ZDQ2ZWY5ZTliYzZlNGIwN2Y4NDgxMmJiMDg0YTVlODRhODdjZDdhYTNlMmE1MGRhY2JmNzVmYzFjYjRjIn0%3D; _ga_FFYVNFBC5R=GS1.1.1658305132.2.1.1658306702.0',
            'dnt': '1',
            'referer': 'https://www.tuberslab.com/notes',
            'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
            'x-xsrf-token': 'eyJpdiI6InNWWHA5NzJEeDlxOVNtK2YrOGx2dmc9PSIsInZhbHVlIjoiSHR4V1JtNTRcL0FDYzNJNnR5Z1NGWVlxMFRCd3JjUDkyUTBoNFpscVJxUDlaUCtFVzFBTXhYMWUrZVEwZnBEYkJYNklGWHNkQllld3NKTEJtS1FNWEZRTWxYbXUxZ1JVd3ExazloS0xaMnBhWVRZYis1REgrXC9DUFN2MVdzZU9LTSIsIm1hYyI6IjI1ZDUzMDJkODRhNDVhNjdkYjA2OTk3YzliY2RkZDcyYjNkNGY2ZDU0ZGYyMWM4ZjAyNDZhYTM3NjZjMDMwZmIifQ==',
        }   
        print("Using bertha system")

    else:
        cookies = {
            'ai_user': 'oCrEpuLb0jCIgH+7NtJpvR|2022-07-15T10:56:11.506Z',
            '_ga': 'GA1.1.1919492163.1657882572',
            '_hjSessionUser_1930158': 'eyJpZCI6IjgwNGVkMDEwLTU0OGQtNWYxYS1hMzk2LTdmOWQxMGNjMjk1ZSIsImNyZWF0ZWQiOjE2NTc4ODI1NzI0MTEsImV4aXN0aW5nIjp0cnVlfQ==',
            '_hjIncludedInSessionSample': '1',
            '_hjSession_1930158': 'eyJpZCI6ImVmNGJmMjk3LTYxYzUtNDAwNi05NTBjLTIxZjI2MTY2NWFjOSIsImNyZWF0ZWQiOjE2NTc5MDExNDQxODcsImluU2FtcGxlIjp0cnVlfQ==',
            'remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d': 'eyJpdiI6ImNsZUhzaVl3Qjd6bkxLT0kwRnpDR1E9PSIsInZhbHVlIjoiamFtK3BoVzQ4dTNyN2xOV3VhZ1U5Q0Z2TjEwYWNkc1BoRnZvNjZCSlBUZ21cL0E2UDB6cmY2OUt5WnIxQjBQeW1rY3VNZ2xKRGRXVkZSbEZDK2FudlFMN29oSkxlcHJES1wvUDFDY29xc1E1S0dIQ041VW44TFwvaTVMMlwvend3MmtyWmpkR1QzZ0tHbmNyVjF0b0xwcjFCXC9iU3JOTWlZemRqRFdtRSt1bWJCY0dTcmNrYkdjeE1ObEFhUlZ6a1dxQUt2MzdjVlVWUTZ3Nm9oS2dvY0xHNzVnYndmR1wvblp2OEJXQ2hqOGhta0pJYz0iLCJtYWMiOiJiMmZkMDE4MGFhZTc0ODVkZWE3ZGZiZDJlNjRmNjRkN2NmMDg5YzFjZTI2NjdlMTkzOWFkZjEyZDc3NTY1MzUyIn0%3D',
            'XSRF-TOKEN': 'eyJpdiI6IkYxQVgwZE1zY0hFVlNjYUhSNksxSlE9PSIsInZhbHVlIjoieGhcL1g4aGdxTVNxMGV5VThmbytScm92blEwanNjZis1eWR4NjlEa3RldFwvOGZ5ZWVSRTErZzUyWHpOVXpwZGlidnV0dDYrOHF4d1pNTm5SN0xCWXRwSzZSR1JqZTl4NVRjNGgxT25PQlF6d0dTclJXNDd1Qjd1RGtNZzRPTUFaMCIsIm1hYyI6IjBkYzc1NjcxZTI3MDE1ZTE3ZDJmNjI2YmY1OWQyMWFiODQ5ODcwZjg3NGJlOWZmZjI5MzE5Nzc2ZTBhNGE4N2UifQ%3D%3D',
            'tuberslab_session': 'eyJpdiI6InRMeGNVSUdNdE9rVURFVVMzcWpZdmc9PSIsInZhbHVlIjoiZmFGczRJSStQa2tCTzE2N1ZkTjFBQzJ5VkRoZWRLNCtyd0V0WVNUTkgxNWlkalVPb0s2d3k0WU1IS3o1NWU5dElsZFdSdktObk9IXC9xSlJrOUF5WXVpRUI3MnUzTFhyTG9NWUlHU0ZSKzB0NDFmdGxEUzB1bnlKNzdxTklaTk5LIiwibWFjIjoiZjVlN2U4MmMzOTMyNDZkZDRhYzc2OTQ1MGVjMWViM2QyMmFhOWE1ODhhYjY3OTBhMTFlNmM3MDdjZDVkYjEyZSJ9',
            '_ga_FFYVNFBC5R': 'GS1.1.1657901142.3.1.1657901171.0',
        }

        headers = {
            'authority': 'www.tuberslab.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9,fr-FR;q=0.8,fr;q=0.7,da;q=0.6',
            # Requests sorts cookies= alphabetically
            # 'cookie': 'ai_user=oCrEpuLb0jCIgH+7NtJpvR|2022-07-15T10:56:11.506Z; _ga=GA1.1.1919492163.1657882572; _hjSessionUser_1930158=eyJpZCI6IjgwNGVkMDEwLTU0OGQtNWYxYS1hMzk2LTdmOWQxMGNjMjk1ZSIsImNyZWF0ZWQiOjE2NTc4ODI1NzI0MTEsImV4aXN0aW5nIjp0cnVlfQ==; _hjIncludedInSessionSample=1; _hjSession_1930158=eyJpZCI6ImVmNGJmMjk3LTYxYzUtNDAwNi05NTBjLTIxZjI2MTY2NWFjOSIsImNyZWF0ZWQiOjE2NTc5MDExNDQxODcsImluU2FtcGxlIjp0cnVlfQ==; remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d=eyJpdiI6ImNsZUhzaVl3Qjd6bkxLT0kwRnpDR1E9PSIsInZhbHVlIjoiamFtK3BoVzQ4dTNyN2xOV3VhZ1U5Q0Z2TjEwYWNkc1BoRnZvNjZCSlBUZ21cL0E2UDB6cmY2OUt5WnIxQjBQeW1rY3VNZ2xKRGRXVkZSbEZDK2FudlFMN29oSkxlcHJES1wvUDFDY29xc1E1S0dIQ041VW44TFwvaTVMMlwvend3MmtyWmpkR1QzZ0tHbmNyVjF0b0xwcjFCXC9iU3JOTWlZemRqRFdtRSt1bWJCY0dTcmNrYkdjeE1ObEFhUlZ6a1dxQUt2MzdjVlVWUTZ3Nm9oS2dvY0xHNzVnYndmR1wvblp2OEJXQ2hqOGhta0pJYz0iLCJtYWMiOiJiMmZkMDE4MGFhZTc0ODVkZWE3ZGZiZDJlNjRmNjRkN2NmMDg5YzFjZTI2NjdlMTkzOWFkZjEyZDc3NTY1MzUyIn0%3D; XSRF-TOKEN=eyJpdiI6IkYxQVgwZE1zY0hFVlNjYUhSNksxSlE9PSIsInZhbHVlIjoieGhcL1g4aGdxTVNxMGV5VThmbytScm92blEwanNjZis1eWR4NjlEa3RldFwvOGZ5ZWVSRTErZzUyWHpOVXpwZGlidnV0dDYrOHF4d1pNTm5SN0xCWXRwSzZSR1JqZTl4NVRjNGgxT25PQlF6d0dTclJXNDd1Qjd1RGtNZzRPTUFaMCIsIm1hYyI6IjBkYzc1NjcxZTI3MDE1ZTE3ZDJmNjI2YmY1OWQyMWFiODQ5ODcwZjg3NGJlOWZmZjI5MzE5Nzc2ZTBhNGE4N2UifQ%3D%3D; tuberslab_session=eyJpdiI6InRMeGNVSUdNdE9rVURFVVMzcWpZdmc9PSIsInZhbHVlIjoiZmFGczRJSStQa2tCTzE2N1ZkTjFBQzJ5VkRoZWRLNCtyd0V0WVNUTkgxNWlkalVPb0s2d3k0WU1IS3o1NWU5dElsZFdSdktObk9IXC9xSlJrOUF5WXVpRUI3MnUzTFhyTG9NWUlHU0ZSKzB0NDFmdGxEUzB1bnlKNzdxTklaTk5LIiwibWFjIjoiZjVlN2U4MmMzOTMyNDZkZDRhYzc2OTQ1MGVjMWViM2QyMmFhOWE1ODhhYjY3OTBhMTFlNmM3MDdjZDVkYjEyZSJ9; _ga_FFYVNFBC5R=GS1.1.1657901142.3.1.1657901171.0',
            'dnt': '1',
            'referer': 'https://www.tuberslab.com/notes',
            'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
            'x-xsrf-token': 'eyJpdiI6IkYxQVgwZE1zY0hFVlNjYUhSNksxSlE9PSIsInZhbHVlIjoieGhcL1g4aGdxTVNxMGV5VThmbytScm92blEwanNjZis1eWR4NjlEa3RldFwvOGZ5ZWVSRTErZzUyWHpOVXpwZGlidnV0dDYrOHF4d1pNTm5SN0xCWXRwSzZSR1JqZTl4NVRjNGgxT25PQlF6d0dTclJXNDd1Qjd1RGtNZzRPTUFaMCIsIm1hYyI6IjBkYzc1NjcxZTI3MDE1ZTE3ZDJmNjI2YmY1OWQyMWFiODQ5ODcwZjg3NGJlOWZmZjI5MzE5Nzc2ZTBhNGE4N2UifQ==',
        }
        print("Using laptop")
    response = requests.get('https://www.tuberslab.com/api/notes', cookies=cookies, headers=headers)

    json_format = json.loads(response.text)
    #print(type(json_format)) -> dict
    #notes in list format from dict "notes" : [{...}]
    #time in seconds -> 401 -> 6:41
    # create func format_time_stamp(second) -> returns (hour:)minute:second
    raw_data_json = json_format["notes"]
    #iterating through list
    #creating dataframe
    
    for note_group in raw_data_json:
        # note_texts and time_stamps contained in list
        raw_notes = json.loads(note_group["notes"])
        #converting them into key/value pairs
        notes = {}

        for note in raw_notes:
            time_stamp = format_time_stamp(note["time"])
            note_text = note["note"]
            # time stamp key, note_text value
            notes[time_stamp] = note_text
        
        #all data needed from request
        c.execute("INSERT OR REPLACE INTO video_notes (thumbnail, title, summary_html_format, updated_at, created_at, id, notes) VALUES (?, ?, ?, ?, ?, ?, ?);", (note_group["medium_thumbnail"], note_group["title"], note_group["html_summary"], note_group["updated_at"], note_group["created_at"], int(note_group["id"]), str(notes)))
        conn.commit()
    """data = {
        "thumbnail" : note_group["medium_thumbnail"],
        "title" : note_group["title"],
        "summary_html_format" : note_group["html_summary"],
        "updated_at" : note_group["updated_at"],
        "created_at" : note_group["created_at"],
        "video_id" : note_group["video_id"],
        "id" : note_group["id"],
        "notes" : notes
    }"""
    return 0


# retrieve the data from time_tracker table
def get_db(date="all", category=None, ascending=False):
    conn = sqlite3.connect("app_database")
    c = conn.cursor()

    #print(formatted_date)
    
    

    if ascending:
        if date == "all":
            time_data = c.execute("SELECT * FROM time_tracker ORDER BY date ASC, time ASC;")
            conn.commit()
        else:
            time_data = c.execute("SELECT * FROM time_tracker WHERE date=? ORDER BY date DESC, time ASC;", (date, ))
            conn.commit()
    else:
        if date == "all":
            time_data = c.execute("SELECT * FROM time_tracker ORDER BY time DESC;")
            conn.commit()
        else:
            time_data = c.execute("SELECT * FROM time_tracker WHERE date=? ORDER BY time DESC;", (date, ))
            conn.commit()


    list_of_rows = []

    for row in time_data:
        # converting tuple into list
        intermediary_list = []
        for i in row:
            intermediary_list.append(i)

        

        if category != None:

            # appends entry only if category appears in entry
            if category in intermediary_list[4]:
                list_of_rows.append(intermediary_list)
            
        else:
            
            list_of_rows.append(intermediary_list)
    
    #classify_data(merge_data(list_of_rows))
    return list_of_rows
    

# app taken every 10 secs. If the same across intervals, merge two together.
def merge_data(db):
    # assuming db has the form of list of lists

    new_db = []
    # storing prev_entry to compare app against
    prev_entry = []
    counter = 0

    for i in db:
        # storing initial var
        if prev_entry == []:
            prev_entry = i
        else:
            # if third entry in each list is similar enough (90% resemblance) to prev., merge
            # 
            # print(prev_entry[2], i[2], "Similarity : ", similar(prev_entry[2], i[2]))
            if similar(prev_entry[2], i[2]) >= 0.9:
                
                # also, only merge if less than an hour between the two
                if (to_seconds(i[1]) - to_seconds(prev_entry[1])) < 3600:
                    # print(to_seconds(i[1]) - to_seconds(prev_entry[1]))
                # if they are equal, update time_stamp to last one
                    #print(to_seconds(i[1]) - to_seconds(prev_entry[1]))
                    prev_entry[1] = i[1]        
            # else, new one, so append prev. one as it cannot be merged further
            else:
                # print("Appending", prev_entry)
                new_db.append(prev_entry)
                prev_entry = i
        
        counter += 1

    # finally, store the last entry
    new_db.append(prev_entry)

    # creating new table for it and deleting prev. one to save storage
    # without losing information

    # just in case, creating backup that is deleted at the end of func
    c.execute("CREATE TABLE backup AS SELECT * FROM time_tracker;")
    conn.commit()

    succesful = c.execute("DROP TABLE time_tracker;")

    # deleting entries somehow doesn't disturb the background program
    conn.commit()

    create_db()
    conn.commit()

    for entry in new_db:
        try:
            c.execute("INSERT INTO time_tracker (date, time, window_name, app, activities, link) VALUES\
                (?, ?, ?, ?, ?, ?);", (entry))
            conn.commit()
        except:
            print(entry)
    
    # deleting temporary safeguard now that the new one has been created
    c.execute("DROP TABLE backup;")
    conn.commit()
    return new_db

# group something like Chrome activity into "Web browsing",
# vs code in "Coding" etc.
# ultimately, for gantt chart using matplotlib
# taking db as list_of_lists
def classify_data(db):
    # assuming db as list_of_lists

    # storing possible activities-groups
    # not mutually exclusive
    # entertainment, i.e. youtube and web browsing will overlap
    # stored along with their identifier
    # for example, youtube by "youtube.com" in link
    # obviously not full-proof, but it should be decent

    df = pd.DataFrame(db, columns=TIME_TRACKER_COLUMNS)
    
    
    categorised_dict = {}
    for i in ACTIVITES.keys():
        categorised_dict[i] = []

    """
    Loop through each entry
        Loop through each possible activity
            If identifier contained in window, app or link
                If active_status is False
                    Store time_start in list in df as ["Start", date, time of current entry checked]
                    active = True
                Else:
                    pass
            Else
                If active_status is True
                    store time_end in df as ["End", date, time of current entry checked]
                    active = False
        
    """
    for i in range(df.shape[0]):
        
        for j in categorised_dict:
            
            activity_name = j
            activity_identifiers = ACTIVITES[activity_name][0]
            active_status = ACTIVITES[activity_name][1]

            for activity_identifier in activity_identifiers:
                # print(activity_identifier, df["window_name"][i], activity_identifier in df["window_name"][i], df["app"][i], activity_identifier in df["app"][i], df["link"][i], activity_identifier in df["link"][i])
                if (activity_identifier in df["window_name"][i]) or (activity_identifier in df["app"][i]) or (activity_identifier in df["link"][i]):
                    # debug 
                    # print("Present", activity_identifier, df["window_name"][i], df["app"][i], df["link"][i])
                    if active_status == False:
                        categorised_dict[activity_name].append(["Start", df["date"][i], df["time"][i]])
                        ACTIVITES[activity_name][1] = True
                        break
                
                # only triggers if last iteration of identifiers. Otherwise, it could run into some funky scenarios.
                else:
                    if activity_identifier == activity_identifiers[-1]:
                        # debug
                        # print("Missing", activity_identifier, df["window_name"][i], df["app"][i], df["link"][i])
                        # print(activity_identifier in df["link"][i], type(str(df["link"][i])))

                        if active_status == True:
                            categorised_dict[activity_name].append(["End", df["date"][i], df["time"][i]])
                            ACTIVITES[activity_name][1] = False

    return categorised_dict


now = datetime.now()
today = now.strftime("%Y-%m-%d")

# gantt_chart visualisatino of time_tracker table
def gantt_chart(date, categorised_data, hour_minute="", start_hour="", end_hour="", show=False):
    # assuming categorised_data as dict with keys of activities

    # safeguard in case category is selected on time_tracker
    if date == "all":
        date = today


    activities = categorised_data.keys()

    y_counter = 0


    ##### customising figure ###
    fig, ax = plt.subplots(1)

    COLORS = ["r", "b", "g", "c", "k", "w", "m", "y"]

    y_pos = np.arange(len(activities))

    ax.set_yticks(y_pos, labels=activities) # , 
    ax.invert_yaxis()

    x_ticks_pos = []
    x_ticks_labels = []
    for i in range(24):
        x_ticks_pos.append(i*3600)
        if i<10:
            time_formatted = f"0{i}:00"
        else:
            time_formatted = f"{i}:00"
        x_ticks_labels.append(time_formatted)


    ax.set_xticks(x_ticks_pos, x_ticks_labels)

    if start_hour != "" and end_hour != "":
       plt.xlim([start_hour * 3600, end_hour * 3600])

    ax.set_xlabel("Time")
    ax.set_title("Time spent on computer, " + date)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.tick_params(axis='x', which='major' , labelsize=5, labelcolor='green')

    ########


    # looping through dict
    for i in activities:
        start = ""
        end = ""
        for j in categorised_data[i]:
            start_or_end, date, time = j

            if start_or_end == "Start":
                start = to_seconds(time)
            else:
                try:
                    # graph it, and reset counters.
                    end = to_seconds(time)

                    time_difference = end - start

                    #graphing
                    ax.barh(y_counter, time_difference, align="edge", left=start, height=0.3, color=COLORS[y_counter % len(COLORS)])
                    # resetting
                    start = ""
                    end = ""
                except:
                    pass

        y_counter += 1
    filepath = "static\\time_spent\\" + date + hour_minute + ".png"
    if os.path.exists(filepath):
        print("Replacing existing file", filepath)
        os.remove(filepath)
    
    if show:
        plt.show()
    else:
        plt.savefig(filepath, dpi=300)
    
# converts %H:%M:%S to pure seconds
def to_seconds(time_string):
    # format %H:%M:%s
    time = time_string.split(":")
    seconds = 0
    seconds += int(time[0]) * 3600
    seconds += int(time[1]) * 60
    seconds += int(time[2])
    return seconds

# gets current date and nb_days next days (nb_days including today) (formatted)
def get_days(nb_days):
    dates = [date.today()]
    for i in range(1, nb_days):
        ith_day = dates[0] + timedelta(days=i)
        dates.append(ith_day)
    #formatting them all
    # format, "Friday, Nov 13th
    for i in range(len(dates)):
        dates[i] = calendar.day_name[dates[i].weekday()] + ", " + dates[i].strftime("%b. %d")

        # debug print(dates[i])
    return dates

# formatted for sql
def get_days_sql(nb_days):
    dates = [date.today()]
    for i in range(1, nb_days):
        ith_day = dates[0] + timedelta(days=i)
        ith_day = ith_day.strftime("%Y-%m-%d")
        dates.append(ith_day)
    dates[0] = dates[0].strftime("%Y-%m-%d")
    return dates


# format seconds into (hour:)minute:seconds
def format_time_stamp(time):
    if type(time) != int:
        print("Converting into integer")
        time = int(time)


    hour = time // 3600
    time = time - hour* 3600
    
    minute = time // 60
    time = time - minute * 60

    second = time
    if hour == 0:
        return (f"{minute}:{second}")
    else:
         return (f"{hour}:{minute}:{second}")


#gantt_chart(today, classify_data(get_db()), show=True, start_hour=8, end_hour=14)

merge_data(get_db(ascending=True))

try:
    update_db()
# no internet
except:
    print("No internet. Not fetching new data from TubersLab API")
