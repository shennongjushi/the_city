import cgi
import urllib
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import files, images
from google.appengine.api import mail
from datetime import *
from api import *
import webapp2
import json
import httplib
import urllib
import api
import mimetypes
import base64
import os
import jinja2
import re
import random
import urllib2
import httplib2
import logging
import pickle
from apiclient import discovery
from oauth2client import appengine
from oauth2client import client
from google.appengine.api import memcache

def larger0(someitem):
    return someitem > 0

def larger1(someitem):
    return someitem > 1
def larger2(someitem):
    return someitem > 2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
JINJA_ENVIRONMENT.tests["larger0"] = larger0
JINJA_ENVIRONMENT.tests["larger1"] = larger1
JINJA_ENVIRONMENT.tests["larger2"] = larger2

##########################################
#           Google Calendar Plugin       #
##########################################
# CLIENT_SECRETS, name of a file containing the OAuth 2.0 information for this
# application, including client_id and client_secret, which are found
# on the API Access tab on the Google APIs
# Console <http://code.google.com/apis/console>
CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')

# Helpful message to display in the browser if the CLIENT_SECRETS file
# is missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
<h1>Warning: Please configure OAuth 2.0</h1>
<p>
To make this sample run you will need to populate the client_secrets.json file
found at:
</p>
<p>
<code>%s</code>.
</p>
<p>with information found on the <a
href="https://code.google.com/apis/console">APIs Console</a>.
</p>
""" % CLIENT_SECRETS

http = httplib2.Http(memcache)
service = discovery.build("calendar", "v3", http=http)
decorator = appengine.oauth2decorator_from_clientsecrets(
    CLIENT_SECRETS,
    #scope='https://www.googleapis.com/auth/plus.me',
    scope='https://www.googleapis.com/auth/calendar',
    message=MISSING_CLIENT_SECRETS_MESSAGE)

#####################################################
#		Google Calendar Plugin		    #
#####################################################

class Index(webapp2.RequestHandler):
    def get(self):
        music_activity = list()
        movie_activity = list()
        travel_activity = list()
        food_activity = list()
        hot_activities = 0
        music = 0
        movie = 0
        travel = 0
        food = 0
        activities = Activity.query().order(-Activity.hot_number).fetch()
        if (len(activities)>3):
            hot_activities = 3
        else:
            hot_activities = len(activities)
        for activity in activities:
            print activity.hot_number
            if (activity.tag.lower() == "music"):
                music_activity.append(activity)
            elif (activity.tag.lower() == "movie"):
                movie_activity.append(activity)
            elif (activity.tag.lower() == "travel"):
                travel_activity.append(activity)
            elif (activity.tag.lower() == "food"):
                food_activity.append(activity)
        if (len(music_activity)>4):
            music = 4
        else:
            music = len(music_activity)
        if (len(movie_activity)>4):
            movie = 4
        else:
            movie = len(movie_activity)
        if (len(travel_activity)>4):
            travel = 4
        else:
            travel = len(travel_activity)
        if (len(food_activity)>4):
            food = 4
        else:
            food = len(food_activity)
        user = users.get_current_user()
	if user:
            user_query = ndb.Key(Webusers,user.email()).get()
	    if not user_query:
	        self.redirect('/profile_create')
	    else:
                logout_url = users.create_logout_url('/')
	        template_value = {
	    	'user': user,
	    	'nickname':user_query.nickname,
		'logout_url':logout_url,
                'activities':activities,
                'hot_activities':hot_activities,
                'music':music,
                'music_activity':music_activity,
                'food':food,
                'food_activity':food_activity,
                'movie':movie,
                'movie_activity':movie_activity,
                'travel':travel,
                'travel_activity':travel_activity,
	        }
		template = JINJA_ENVIRONMENT.get_template('index.html')
		self.response.write(template.render(template_value))
	else:
	    login_url = users.create_login_url('/')
	    template_value = {
		'user': user,
		'login_url':login_url,
                'activities':activities,
                'hot_activities':hot_activities,
                'music':music,
                'music_activity':music_activity,
                'food':food,
                'food_activity':food_activity,
                'movie':movie,
                'movie_activity':movie_activity,
                'travel':travel,
                'travel_activity':travel_activity,
	    }
	    template = JINJA_ENVIRONMENT.get_template('index.html')
	    self.response.write(template.render(template_value))
	

class Post_activity(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
	if not user:
	    self.redirect(users.create_login_url('/post'))
	else:
	    upload_url = blobstore.create_upload_url('/api/post')
	    print upload_url
	    print user.email()
	    template_value = {
	        'upload_url':upload_url,
		'user': user.email()
	    }
	    template = JINJA_ENVIRONMENT.get_template('post.html')
	    self.response.write(template.render(template_value))

class Profile_create(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
	if not user:
	    self.redirect(users.create_login_url('/profile_create'))
	else:
	    user_query = ndb.Key(Webusers, str(user.email())).get()
	    if not user_query:
	        profile_url = blobstore.create_upload_url('/api/profile')
	        template_value = {
	            'profile_url': profile_url,
	            'user': user.email() 
	        }
	    	template = JINJA_ENVIRONMENT.get_template('profile_create.html')
	        self.response.write(template.render(template_value))
	    else:
		self.redirect('/my_city')
	#else
class Profile_edit(webapp2.RequestHandler):
    def get(self):
	user = users.get_current_user()
	if not user:
	    self.redirect(users.create_login_url('/profile_edit'))
	else:
	    user_query = ndb.Key(Webusers, str(user.email())).get()
	    if not user_query:
		self.redirect('/profile_create')
	    else:
		profile_url = blobstore.create_upload_url('/api/profile')
		if user_query.birthday:
		    birthday = str(user_query.birthday.year) + '/'+str(user_query.birthday.month) + '/' + str(user_query.birthday.day)
		else:
		    birthday = ''
		template_value = {
		    'user':user.email(),
		    'profile_url':profile_url,
		    'nick':user_query.nickname,
		    'gender':user_query.gender,
		    'birthday':birthday,
		    'introduce':user_query.introduce,
		    'interest':user_query.interest
		}
	    	template = JINJA_ENVIRONMENT.get_template('profile_edit.html')
	        self.response.write(template.render(template_value))
#My city
class My_city(webapp2.RequestHandler):
    def get(self):
	user = users.get_current_user()
	if not user:
	    self.redirect(users.create_login_url('/my_city'))
	else:
	    requests = {
		'user_id':str(user.email())
	    }
            headers = {"Content-type": "application/json", "Accept": "text/plain"}
            conn = httplib.HTTPConnection("localhost","8888")
            conn.request("POST", "/api/person", json.dumps(requests), headers)
            responses = conn.getresponse()
	    #Get date
	    nick = ''
	    take_activity = list()
	    like_activity = list()
	    post_activity = list()
	    introduce = ''
	    photo = ''
	    gender = ''
	    interest_tag = list()
	    sub_me_number = 0
	    greetings_author=list()
	    greetings_content = list()
	    greetings = list()
            login_url = users.create_login_url(self.request.uri)
            if responses.status == 200:
		data = json.loads(responses.read())
		photo = data['photo']
		taken = data['taken']
		like = data['like']
		post = data['post']
		nick = data['nick']
		gender = data['gender']
		introduce = data['introduce']
		interest = data['interest']
		sub_me_number = data['sub_me_number']
		greetings = Greeting_person.query(ancestor=ndb.Key(Webusers, str(user.email()))).order(Greeting_person.date).fetch()
		for activity in taken:
		    take_activity.append(ndb.Key(Activity, long(activity)).get())
		for activity in like:
		    like_activity.append(ndb.Key(Activity, long(activity)).get())
		for activity in post:
		    post_activity.append(ndb.Key(Activity, long(activity)).get())
		for tag in interest:
		    interest_tag.append(str(tag))
	    template_value = {
		'nick': nick,
		'take_activity':take_activity,
		'like_activity':like_activity,
		'post_activity':post_activity,
		'introduce':introduce,
		'interest':interest_tag,
		'sub_me_number':sub_me_number,
		'len_interest':len(interest_tag),
		'gender':gender,
		'photo':photo,
		'user': user.email(),
		'guest': user.email(),
		'greetings':greetings,
		'login_url':login_url,
	    }
	    template = JINJA_ENVIRONMENT.get_template('my_city.html')
	    self.response.write(template.render(template_value))
	
class Image_Show(blobstore_handlers.BlobstoreDownloadHandler):
   def get(self):
       blob_key = self.request.get('key')
       blob_info = blobstore.BlobInfo.get(str(urllib.unquote(blob_key)))
       self.send_blob(blob_info)

class Person(webapp2.RequestHandler):
    def get(self):
	user = self.request.get('user')
	guest = users.get_current_user()
	guest_id = ''
	flag = 0
	if guest: 
	    if user == guest.email():
		flag = 1
	        self.redirect('/my_city')
	    guest_id = guest.email()
	if flag == 0:
	    requests = {
		'user_id':str(user)
	    }
            headers = {"Content-type": "application/json", "Accept": "text/plain"}
            conn = httplib.HTTPConnection("localhost","8888")
            conn.request("POST", "/api/person", json.dumps(requests), headers)
            responses = conn.getresponse()
	    #Get date
	    nick = ''
	    take_activity = list()
	    like_activity = list()
	    post_activity = list()
	    introduce = ''
	    photo = ''
	    gender = ''
	    interest_tag = list()
	    greetings_author=list()
	    greetings_content = list()
	    sub_me_number = 0
            if responses.status == 200:
		data = json.loads(responses.read())
		photo = data['photo']
		taken = data['taken']
		like = data['like']
		post = data['post']
		nick = data['nick']
		gender = data['gender']
		introduce = data['introduce']
		interest = data['interest']
		sub_me_number = data['sub_me_number']
		for activity in taken:
		    take_activity.append(ndb.Key(Activity, long(activity)).get())
		for activity in like:
		    like_activity.append(ndb.Key(Activity, long(activity)).get())
		for activity in post:
		    post_activity.append(ndb.Key(Activity, long(activity)).get())
		for tag in interest:
		    interest_tag.append(str(tag))
		greetings = Greeting_person.query(ancestor=ndb.Key(Webusers, str(user))).order(Greeting_person.date).fetch()
	    template_value = {
		'nick': nick,
		'take_activity':take_activity,
		'like_activity':like_activity,
		'post_activity':post_activity,
		'introduce':introduce,
		'interest':interest_tag,
		'sub_me_number':sub_me_number,
		'len_interest':len(interest_tag),
		'gender':gender,
		'photo':photo,
		'user': user,
		'guest': guest_id,
		'greetings':greetings
	    }
	    template = JINJA_ENVIRONMENT.get_template('person.html')
	    self.response.write(template.render(template_value))

class Activity_page(webapp2.RequestHandler):
    @decorator.oauth_aware
    def get(self):	    
	guest_id = ''
	user = users.get_current_user()
	if user:
	    guest_id = user.email()
	activity_id = str(self.request.get('id'))
        requests = {
	'activity_id':activity_id,
	'guest_id': guest_id
	}
	comments = Activity_comment.query(ancestor=ndb.Key(Activity, long(activity_id))).order(Activity_comment.date).fetch()
        headers = {"Content-type": "application/json", "Accept": "text/plain"}
        conn = httplib.HTTPConnection("localhost","8888")
        conn.request("POST", "/api/activity", json.dumps(requests), headers)
        responses = conn.getresponse()
        if responses.status == 200:
	    data = json.loads(responses.read())
	    print "host" + data['host_photo']
	    #guest
	    all_guests = list()
	    all_users = Webusers.query().fetch()
	    for user in all_users:
		if str(activity_id) in user.take_activity:
		    all_guests.append(user)
	    if len(all_guests)%3!=0:
		rows = len(all_guests)/3 + 1
	    else:
		rows = len(all_guests)/3
	    guests_len = len(all_guests)
	####### google_calendar_date_calculate ######
	    calendar_start = data['calendar_start']
	    calendar_end = data['calendar_end']
	    google_calendar_url="https://www.google.com/calendar/render?dates="+calendar_start+"/"+calendar_end+"&details=activity:+http://olenew2014.appspot.com/activity?id="+str(activity_id)+"&text="+data['title']+"&action=TEMPLATE&sprop=http://olenew2014.appspot.com/activity?id="+str(activity_id)+"&trp=False&location="+data['address']+"&sf=true&output=xml#f"
	    template_value = {
	    	'title': data['title'],
		'start_date':data['start_date'],
		'end_date':data['end_date'],
		'neighborhood':data['neighborhood'],
		'zipcode':data['zipcode'],
		'address':data['address'],
		'latitude':data['latitude'],
		'longitude':data['longitude'],
		'host':data['host'],
		'tag':data['tag'],
		'details':data['details'],
		'like_number':data['like_number'],
		'take_number':data['take_number'],
		'cover':data['cover'],
		'date':data['date'],
		'host_photo':data['host_photo'],
		'host_nick':data['host_nick'],
		'activity_id':str(self.request.get('id')),
		'guest': guest_id,
		'like_action':data['like_action'],
		'take_action':data['take_action'],
		'all_date':data['all_date'],
		'more':len(data['all_date'])-1,
		'comments':comments,
		'all_guests':all_guests,
		'guests_len':guests_len,
		'rows':rows,
        	'authorize_url': decorator.authorize_url(),
        	'has_credentials': decorator.has_credentials(),
		'google_calendar_url':google_calendar_url,
	    }
	    print "like_action:" + str(data['like_action'])
	    template = JINJA_ENVIRONMENT.get_template('activity.html')
	    self.response.write(template.render(template_value))
	    
	    
class All_Activity(webapp2.RequestHandler):
    def get(self):
        activities = Activity.query().order(Activity.start_date).fetch()
        music_cover = list()
        music_title = list()
        music_activity = list()  
        food_cover = list()
        food_title = list()
        food_activity = list()
        movie_cover = list()
        movie_title = list()
        movie_activity = list()
        travel_cover = list()
        travel_title = list()
        travel_activity = list()
        other_cover = list()
        other_title = list()
        other_activity = list()
        for activity in activities:
            if(activity.tag.lower()=="music"):
                music_cover.append(activity.cover)
                music_title.append(activity.title)
                music_activity.append(activity)
            elif(activity.tag.lower()=="food"):
                food_cover.append(activity.cover)
                food_title.append(activity.title)
                food_activity.append(activity)
            elif(activity.tag.lower()=="movie"):
                movie_cover.append(activity.cover)
                movie_title.append(activity.title)
                movie_activity.append(activity)
            elif(activity.tag.lower()=="travel"):
                travel_cover.append(activity.cover)
                travel_title.append(activity.title)
                travel_activity.append(activity)
            else:
                other_cover.append(activity.cover)
                other_title.append(activity.title)
                other_activity.append(activity)
        music_counter = len(music_cover)
        food_counter = len(food_cover)
        movie_counter = len(movie_cover)
        travel_counter = len(travel_cover)
        other_counter = len(other_cover)
        print music_counter
        template_value = {
                'music_counter':music_counter,
                'music_cover':music_cover,
                'music_title':music_title,
                'music_activity':music_activity,
                'food_counter':food_counter,
                'food_cover':food_cover,
                'food_title':food_title,
                'food_activity':food_activity,
                'movie_counter':movie_counter,
                'movie_cover':movie_cover,
                'movie_title':movie_title,
                'movie_activity':movie_activity,
                'travel_counter':travel_counter,
                'travel_cover':travel_cover,
                'travel_title':travel_title,
                'travel_activity':travel_activity,
                'other_counter':other_counter,
                'other_cover':other_cover,
                'other_title':other_title,
                'other_activity':other_activity,

        }
        template =  JINJA_ENVIRONMENT.get_template('all_activities.html')
        self.response.write(template.render(template_value))

		

application = webapp2.WSGIApplication([
	('/post', Post_activity),
	('/profile_create', Profile_create),
	('/profile_edit', Profile_edit),
	('/my_city', My_city),
	('/', Index),
	('/img', Image_Show),
	('/person', Person),
	('/activity',Activity_page),
        ('/all_activities',All_Activity),
        ('/search',Search)
        (decorator.callback_path, decorator.callback_handler()),
], debug = True)
















