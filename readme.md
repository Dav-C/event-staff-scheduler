# Event Staff Scheduler (ESS)

Event Staff Scheduler is a tool for scheduling and managing online or in-person 
events (webcast, training etc.) and the team members assigned to run those events.
It is designed for use with a high volume of events, but any number of events 
can be tracked.

#### Browser Compatibility
- Chrome is the only officially supported browser. <br/>
- The UI is responsive and requires a minimum width of 945px.

### Running the app via the Django development server
- Clone the repo
- Install requirements.txt with <code>pip install -r requirements.txt</code> 
  Using a virtual environment is recommended.
- from the terminal, run <code>python manage.py migrate</code>
- create a super user with <code>python manage.py createsuperuser</code>
- start the development server with <code>python manage.py runserver</code>
- The development server can be stopped with <code>CTRL+C</code> 

### Create groups and users with the admin
**NOTE:**  
The app will display different pages to "Team Members" and "Team Managers."   
Team members should be part of a group titled **team_members** and should
**not** have the "is staff" option selected. The **team_members** group will need to be 
created manually.  Team managers should not be in a group and should have 
"is staff" checked.

- navigate to <code>127.0.0.1:8000/admin</code> and login to the admin using the 
  super user credentials 
- create a group titled **team_members**
- Create managers and team members as desired using the information in the note
  above
  
### Access the app and login
- Navigate to <code>127.0.0.1:8000/login</code> and login to the app.  The pages
  available to you will depend on if the logged-in user is a team member or 
  team manager.

### Using the app as a Team Manager
#### The Event Schedule
After logging in, Team managers will be presented with the event schedule.  This page
displays all scheduled events in a rolling 30-day window starting with the current date.
Events do not exist until manually created, this can be done with the Create Event button 
in the options bar at the top of the page.

Days of the week are color coded so groups of days can easily be seen.  All displayed 
times will be based on the user's preferred time zone which will default to US/Pacific 
until changed in the options bar.  Once changed this preference will be retained 
for future logins.

Team members assigned to an event are displayed in the box to the right of the event 
times and only first and last initials will be shown. The remaining columns display 
event type, event status, released/restricted status and notes.

Events can be edited or deleted by clicking on the event title. 

The schedule can be filtered and searched using the various search fields in the
options bar.

Events can either be **Released** or **Restricted**.  Released events will appear on 
all team members schedules, restricted events will not.  The purpose of this feature
is to allow team managers to create and track events but not release the schedule
to the team until it is finalized.

#### Team Messages
Team messages can be created and edited from the team message panel which can be
opened with the team message button in the options bar on the event schedule page.  
Team managers can create, edit and delete messages while team members can only 
view messages.

#### The Planning Page
The planning page can be accessed with the dropdown menu in the upper right-hand 
corner of any page or from buttons on various other pages where appropriate.
There are two sections to the planning page, an upper block and a lower block.

  - ##### Planning Page - Upper Block
    The upper block consists of three insight boxes.  The two on the left show 
    the total number of events assigned to each team member and event counts by
    type.  These counts will affected by the selected month and all active filters.
    <br/>
    The insight box on the far right allows team managers to release or restrict 
    events by date range.  This allows large numbers of events to be released
    or restricted quickly.  The total number of events that can be released or 
    restricted at once is limited to 500.  The total count of released and 
    restricted courses is displayed by month for the current year.
    
  - ##### Planning Page - Lower Block
    The lower block of the planning page contains a calendar of the month selected
    in the options bar.  Each day on the calendar shows all scheduled events 
    by time, separated by event type.  To jump to the details for a particular 
    day, click on the date button at the top of the appropriate calendar day box.
    
### Using the app as a Team Member

Team members are presented with the event schedule after logging in, but it is
different compared to the team manager event schedule view.  There is a new field 
on the end of each event that contains team member notes.  Team member notes can 
only be seen and edited by team members assigned to an event.  

Team members can only see events that are **released**.  All team members can see
all released events.

Team members cannot create or delete events.  When editing an event, team members
can only change the team member notes field.

Team members can view team messages but cannot create, edit or delete them.

Team members do not have access to the planning page.


  




