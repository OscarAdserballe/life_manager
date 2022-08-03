# Life Manager
#### Description: Productivity Flask App

## Screenshots of Web App

#### Register Page
![Homepage](/Demo-screenshots/register.png)

#### Login Page
![Homepage](/Demo-screenshots/login.png)

#### Homepage/Calendar
![Homepage](/Demo-screenshots/calendar.png)

#### Task List Page
![Homepage](/Demo-screenshots/task_list.png)

#### Time Tracker Page
![Homepage](/Demo-screenshots/time-tracker.png)

#### Notes Page
![Homepage](/Demo-screenshots/Notes.png)

#### Video Notes Page
![Homepage](/Demo-screenshots/video_notes.png)

#### Folders Page
![Homepage](/Demo-screenshots/Folders.png)

## Motivation behind the Project

My intention with this project was to create a webapp based on flask that I could use to better manage my day. None of the features developed for this web app are unique, but it's a collection of those things which are useful for me. It's integrated with my chrome extensions in a manner that is not supported by any other apps to my knowledge, or even my time tracker that works across how many devices I choose to support. In no way is it a project that could ever be exported because of this, but it presents a very real personal use cases and it's something I see myself using in the future, perhaps developing it further as my needs change. I could probably have stringed something together that looks similar with a bit of effort in Notion, but this personal project is something I know the ins-and-outs of, while being far more flexible than anything else I might instead use.

Enough with the vague pre-amble... Now I'll actually cover what the project is about in very concrete terms.

## Features [Not Updated! See Screenshots for Better View of Current State of Project]

My "life manager" is an app that has 5 distinct features collected in a minimalist website loosely based on the web app developed for problem set 9 with Finance. The app itself is built using Flask, (Python,) HTML, CSS, Bootstrap, JS, sqlite3, while some of the background apps are predominantly made with Python. It includes,

1. An agenda with a customisable amount of days' schedules shown on the homepage.
2. A collection of notes taken from the different youtube videos I have watched.
3. A task list for those tasks I have to do with no specific time attached in contrast to the agenda on the homepage.
4. A time tracker feature that shows 1) gives an overview of my day's activities in customisable groupings/categories in a gantt chart, 2) and lists the specific apps and pages I've looked at the whole day.
5. A Notes-page that allows me to jot down any thoughts I might have.

#### The Agenda

Perhaps one of the simpler features to implement. This is simply a webpage that allows the user to input a future event and register it to some day and time along with a description. The input is stored in a database that is manipulated using sqlite3 inside the app.py file. Accordingly, based on how many days the user has chosen to view on his home page, the events of the different days are shown on the page.

#### The Video Notes

I've always been really saddened by the fact that some of insights I might feel I got from videos are just slowly lost to time as I forget them. Therefore, I found an extension on Chrome called TubersLab that allowed me to take notes in a panel next to videos that are saved to my TubersLab account. TubersLab then has a page where the user can view their notes taken, which, by investigating hte developer tools and the network activity taking place, we can discover sources its data from an API. By copying the request made to the page in chrome (again in dvp. tools) and inputting it into "curlconverter.com", I can copy-paste the code into python and imitate the request I make in chrome using python and the requests-library. Now it's just a matter of trawling through the JSON-formatted data and storing the relevant information in a table inside the database and displaying it on the user's page.

There are lot of things that can be optimised with this approach and some issues. The most noticable one for me, is the fact that the requests made by chrome to the web page are unique across devices, so there's what feels like a silly if-block testing what device the user is on to make the correct request. But this also necessitates that I repeat the procedure of attaining the correct request to the page for each device.

Despite being an API, it doesn't seem as though it's meant to be accessible. I stumbled on it by sheer luck as I was about to webscrape the page, so I don't know about the legality to make such back-door requests to the API either.

Also, already at this point the webpage is getting impossibly long. There needs to be some modicum of sorting and filtering in what is displayed at some point. Something like drop-down boxes for each video would already be a huge help, but even that is not a viable fix in the long-term.

Originally I had intended to program the extension myself before realising how big an undertaking that was and how unrealistic it was within the time frame I had set for myself.

#### The Task List

Very similar to the "birthdays" page from the problem set, this is just an sqlite3 table which is displayed on a page with delete functionality and insertions possible at the top of the page. Simple, but it really doesn't need any more work than that. The HTML could, however, as is the case with all of these pages as an aside, be improved as sometimes the tasks group up in the same row.

#### The Time Tracker

This was by far the most complicated page to make in all of the app with lots of room for optimisation. Splitting this section up into three categories:

###### Storing the User's activity

By using the win32gui library in python, it was possible to retrieve the foreground window the user had on their screen, which was used as a proxy for what they were doing. Although this assumption works most of the time, there are rare cases where it does not hold, but a compromise had to be made there.

There's more to it, but in broad strokes, I placed a pythonw version of the program in my startup folder so it came up running as soon as my computer started. It keeps looping as it's set up on an event schedule using that library.

Based on the program and the categories dictionary, where each category of activity is associated with a program or substring in a link, the user's type of activity is categorised.

What we end up with is a table storing the user's activity, the app associated with it, the window_name showed in Windows and the link in case it's a google chrome tab, because so much activity is browsing it's nice to get some more detail. All of this is stored in its own table.

###### Displaying the data

![Gantt-Chart](/Demo-screenshots/time-tracker.png)

It was really important to me, that I had a way of seeing in broad strokes how I have spent my day so far, so using matplotlib I create a so-called Gantt-Chart for my activities. Because the things I do and what I want to check for changes with time, I ensured to make it very easy to choose inside the python programs what kind of categories it should display.

Below the table on the website, I also have an HTML-table displaying the individual entries stored inside the time-tracking activities in case I want to trace back what I did at some specific moment. The table rows are also clickable, such that I can refer back to some interesting page or anything of the sort.

#### Notes

Last, and definitely least, is the most bare-bones note-entry page in all of the world. It's literally just a box that allows the user to input a string into a table and then below it displays all previous notes.

## Some Known Issues, Bugs and Possible Optimisations

* Lack of User Input Validation

* No Account Features. This will definitely be an issue if I try to implement on the cloud.

* HTML issues with scaling, most notably with the video notes page

* Youtube Category not working

* Inefficient scaling both in terms of increasing amounts of memory needed for web pages as well as tables and image files that might get a bit out of hand in terms of size.

## Future Plans

This by no means a finished project, nor am I even sure I will ever consider it in such terms. I had hoped to make a functional calendar app that will help me in daily life, and I think achieved that quite well: I waited a few days to test my app before submitting and in that time I've actually found myself using it. The aim was achieved, but I hope to continue to add features as I have time/a need for it.

First and foremost are obviously the issues listed above. But in the longer term I hope to be able to make a cloud-based, more stream-lined version of this app I can access across all my devices.

Implementing notes for my kindle books is on top of my list of features I'm currently working on.

More universally, making a kind of folder system seems a requisite at some point. Both in terms of saving space on the web page, but also for ease of use. If I can make a kind of glorified bookmarks tab where I can assemble all kinds of different notes, I think that would be really useful.

A small quality of life improvement I need to figure out how to do, is how to make the project run more easily. Going into VS Code and typing "flask run" in the terminal is not much work, but it's inconvenient. something like a desktop icon for it would be really nice to have.

Account system! This is such an obvious and small thing,  but man, sitting down and having to rework the tables only makes procrastination easier.

Right now, there's also the feature of kind of "squashing" the entries in the time-tracking table. It needs to be optimised, because currently it goes through the entire table, despite most of it already having been optimised.

There are so many more things to add, but this seems to be an adequate list of the things I find the most pressing to implement. In any case, despite being an arguably incomplete project, I'm really happy with it. This was CS50.
