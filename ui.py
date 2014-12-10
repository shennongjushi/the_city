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
def equals1(someitem):
    return someitem==1

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
JINJA_ENVIRONMENT.tests["larger0"] = larger0
JINJA_ENVIRONMENT.tests["larger1"] = larger1
JINJA_ENVIRONMENT.tests["larger2"] = larger2
JINJA_ENVIRONMENT.tests["equals1"] = equals1

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
        keyword = self.request.get('q')
        if keyword:
            print keyword
            self.redirect('/search?keyword=%s#Undergoing'%keyword)
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
        keyword = self.request.get('q')
        if keyword:
            print keyword
            self.redirect('/search?keyword=%s'%keyword)
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
        keyword = self.request.get('q')
        if keyword:
            print keyword
            self.redirect('/search?keyword=%s'%keyword)
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
        keyword = self.request.get('q')
        if keyword:
            print keyword
            self.redirect('/search?keyword=%s'%keyword)
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
        keyword = self.request.get('q')
        if keyword:
            print keyword
            self.redirect('/search?keyword=%s'%keyword)
	user = users.get_current_user()
	if user:
	    get_user = ndb.Key(Webusers, str(user.email())).get()
	if not user:
	    self.redirect(users.create_login_url('/my_city'))
	elif not get_user:
	    self.redirect('/profile_create')
	else:
	    requests = {
		'user_id':str(user.email())
	    }
            headers = {"Content-type": "application/json", "Accept": "text/plain"}
            conn = httplib.HTTPConnection("the-city.appspot.com")
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
		sub_me = list()
		for people in data['sub_me']:
		    sub_me.append(ndb.Key(Webusers, str(people)).get())
		i_sub = list()
		for people in data['i_sub']:
		    i_sub.append(ndb.Key(Webusers, str(people)).get())
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
		'sub_me_number':len(sub_me),
		'sub_me':sub_me,
		'i_sub':i_sub,
		
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
            conn = httplib.HTTPConnection("the-city.appspot.com")
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
		sub_me = list()
		for people in data['sub_me']:
		    sub_me.append(ndb.Key(Webusers, str(people)).get())

		i_sub = list()
		for people in data['i_sub']:
		    i_sub.append(ndb.Key(Webusers, str(people)).get())
		for activity in taken:
		    take_activity.append(ndb.Key(Activity, long(activity)).get())
		for activity in like:
		    like_activity.append(ndb.Key(Activity, long(activity)).get())
		for activity in post:
		    post_activity.append(ndb.Key(Activity, long(activity)).get())
		for tag in interest:
		    interest_tag.append(str(tag))
		greetings = Greeting_person.query(ancestor=ndb.Key(Webusers, str(user))).order(Greeting_person.date).fetch()
		## subscribe cancel or not##
		guest_query = ndb.Key(Webusers, guest_id).get()
		if user not in guest_query.subscribe:
		    action = 'subscribe'
		elif user in guest_query.subscribe:
		    action = 'unsubscribe'
		   
	    template_value = {
		'nick': nick,
		'take_activity':take_activity,
		'like_activity':like_activity,
		'post_activity':post_activity,
		'introduce':introduce,
		'interest':interest_tag,
		'sub_me_number':len(sub_me),
		'sub_me':sub_me,
		'i_sub':i_sub,
		'len_interest':len(interest_tag),
		'gender':gender,
		'photo':photo,
		'user': user,
		'guest': guest_id,
		'greetings':greetings,
		'action':action 
	    }
	    template = JINJA_ENVIRONMENT.get_template('person.html')
	    self.response.write(template.render(template_value))

class Activity_page(webapp2.RequestHandler):
    @decorator.oauth_aware
    def get(self):	    
        keyword = self.request.get('q')
        if keyword:
            print keyword
            self.redirect('/search?keyword=%s'%keyword)
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
	images = Imag.query(ancestor = ndb.Key(Activity, long(activity_id))).order(Imag.date).fetch()
	image_urls = list()
	for image in images:
	    image_urls.append(image.url)
        headers = {"Content-type": "application/json", "Accept": "text/plain"}
        conn = httplib.HTTPConnection("the-city.appspot.com")
        conn.request("POST", "/api/activity", json.dumps(requests), headers)
        responses = conn.getresponse()
        if responses.status == 200:
	    data = json.loads(responses.read())
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
		'image_urls':image_urls
	    }
	    print "like_action:" + str(data['like_action'])
	    template = JINJA_ENVIRONMENT.get_template('activity.html')
	    self.response.write(template.render(template_value))
	    
	    
class All_Activity(webapp2.RequestHandler):
    def get(self):
        keyword = self.request.get('q')
        flag = 0
        if keyword:
            flag=1
            print keyword
            self.redirect('/search?keyword=%s'%keyword)
        if flag == 0:
            activities = Activity.query().order(Activity.start_date).fetch()
            start_id = self.request.get('start_id')
            if not start_id:
                start_id =1
            print "lllllll"
            print start_id
            print"hhhhhh"
            music_cover = list()
            music_title = list()
            music_activity = list()
            music_start = list()
            music_end = list()
            music_holder = list()
            food_cover = list()
            food_title = list()
            food_activity = list()
            food_start = list()
            food_end = list()
            food_holder = list()
            movie_cover = list()
            movie_title = list()
            movie_activity = list()
            movie_start = list()
            movie_end = list()
            movie_holder = list()
            travel_cover = list()
            travel_title = list()
            travel_activity = list()
            travel_start = list()
            travel_end = list()
            travel_holder = list()
            other_cover = list()
            other_title = list()
            other_activity = list()
            other_start = list()
            other_end = list()
            other_holder = list()
            for activity in activities:
                if(activity.tag.lower()=="music"):
                    music_cover.append(activity.cover)
                    music_title.append(activity.title)
                    music_activity.append(activity)
                    music_start.append(str(activity.start_date.year)+'/'+str(activity.start_date.month)+'/'+str(activity.start_date.day)+' '+str(activity.start_date.hour)+':'+str(activity.start_date.minute))
                    music_end.append(str(activity.end_date.year)+'/'+str(activity.end_date.month)+'/'+str(activity.end_date.day)+ ' '+ str(activity.end_date.hour)+':'+str(activity.end_date.minute))
                    host = ndb.Key(Webusers, str(activity.host)).get()
                    music_holder.append(host)

                elif(activity.tag.lower()=="food"):
                    food_cover.append(activity.cover)
                    food_title.append(activity.title)
                    food_activity.append(activity)
                    food_start.append(str(activity.start_date.year)+'/'+str(activity.start_date.month)+'/'+str(activity.start_date.day)+' '+str(activity.start_date.hour)+':'+str(activity.start_date.minute))
                    food_end.append(str(activity.end_date.year)+'/'+str(activity.end_date.month)+'/'+str(activity.end_date.day)+ ' '+ str(activity.end_date.hour)+':'+str(activity.end_date.minute))
                    host = ndb.Key(Webusers, str(activity.host)).get()
                    food_holder.append(host)
                elif(activity.tag.lower()=="movie"):
                    movie_cover.append(activity.cover)
                    movie_title.append(activity.title)
                    movie_activity.append(activity)
                    movie_start.append(str(activity.start_date.year)+'/'+str(activity.start_date.month)+'/'+str(activity.start_date.day)+' '+str(activity.start_date.hour)+':'+str(activity.start_date.minute))
                    movie_end.append(str(activity.end_date.year)+'/'+str(activity.end_date.month)+'/'+str(activity.end_date.day)+ ' '+ str(activity.end_date.hour)+':'+str(activity.end_date.minute))
                    host = ndb.Key(Webusers, str(activity.host)).get()
                    movie_holder.append(host)
                elif(activity.tag.lower()=="travel"):
                    travel_cover.append(activity.cover)
                    travel_title.append(activity.title)
                    travel_activity.append(activity)
                    travel_start.append(str(activity.start_date.year)+'/'+str(activity.start_date.month)+'/'+str(activity.start_date.day)+' '+str(activity.start_date.hour)+':'+str(activity.start_date.minute))
                    travel_end.append(str(activity.end_date.year)+'/'+str(activity.end_date.month)+'/'+str(activity.end_date.day)+ ' '+ str(activity.end_date.hour)+':'+str(activity.end_date.minute))
                    host = ndb.Key(Webusers, str(activity.host)).get()
                    travel_holder.append(host)
                else:
                    other_cover.append(activity.cover)
                    other_title.append(activity.title)
                    other_activity.append(activity)
                    other_start.append(str(activity.start_date.year)+'/'+str(activity.start_date.month)+'/'+str(activity.start_date.day)+' '+str(activity.start_date.hour)+':'+str(activity.start_date.minute))
                    other_end.append(str(activity.end_date.year)+'/'+str(activity.end_date.month)+'/'+str(activity.end_date.day)+ ' '+ str(activity.end_date.hour)+':'+str(activity.end_date.minute))
                    host = ndb.Key(Webusers, str(activity.host)).get()
                    other_holder.append(host)
            music_next = 0
            food_next = 0
            movie_next = 0
            travel_next = 0
            other_next = 0
            music_counter = len(music_cover)-(int(start_id)-1)*5
            if(music_counter - 5 >0):
                music_counter = 5
                music_next = 1
            food_counter = len(food_cover)-(int(start_id)-1)*5
            if(food_counter - 5 >0):
                food_counter = 5
                food_next = 1
            movie_counter = len(movie_cover)-(int(start_id)-1)*5
            if(movie_counter - 5 >0):
                movie_counter = 5
                movie_next = 1
            travel_counter = len(travel_cover)-(int(start_id)-1)*5
            if(travel_counter - 5 >0):
                travel_counter = 5
                travel_next = 1
            other_counter = len(other_cover)-(int(start_id)-1)*5
            if(other_counter - 5 >0):
                other_counter = 5
                other_next = 1
            print music_counter
            template_value = {
                    'music_next':int(music_next),
                    'food_next':int(food_next),
                    'travel_next':int(travel_next),
                    'other_next':int(other_next),
                    'movie_next':int(movie_next),
                    'start_id':int(start_id),
                    'music_count':music_counter,
                    'music_cover':music_cover,
                    'music_title':music_title,
                    'music_activity':music_activity,
                    'music_start':music_start,
                    'music_end':music_end,
                    'music_holder':music_holder,
                    'food_count':food_counter,
                    'food_cover':food_cover,
                    'food_title':food_title,
                    'food_activity':food_activity,
                    'food_start':food_start,
                    'food_end':food_end,
                    'food_holder':food_holder,
                    'movie_count':movie_counter,
                    'movie_cover':movie_cover,
                    'movie_title':movie_title,
                    'movie_activity':movie_activity,
                    'movie_start':movie_start,
                    'movie_end':movie_end,
                    'movie_holder':movie_holder,
                    'travel_count':travel_counter,
                    'travel_cover':travel_cover,
                    'travel_title':travel_title,
                    'travel_activity':travel_activity,
                    'travel_start':travel_start,
                    'travel_end':travel_end,
                    'travel_holder':travel_holder,
                    'other_count':other_counter,
                    'other_cover':other_cover,
                    'other_title':other_title,
                    'other_activity':other_activity,
                    'other_start':other_start,
                    'other_end':other_end,
                    'other_holder':other_holder,

            }
            template =  JINJA_ENVIRONMENT.get_template('all_activities.html')
            self.response.write(template.render(template_value))

        
class Image_Upload(webapp2.RequestHandler):
    def get(self):
	activity_id = self.request.get('id')
	finish = self.request.get('finish')
	image_upload_url = blobstore.create_upload_url('/api/image_upload')
	template_value = {
		'activity_id':str(activity_id),
		'finish':str(finish),
		'image_upload_url':image_upload_url
	}
        template = JINJA_ENVIRONMENT.get_template('image_upload.html')
        self.response.write(template.render(template_value))

####Just for test ##########
class Search_nearby(webapp2.RequestHandler):
    def get(self):
        template_value = dict()
        template = JINJA_ENVIRONMENT.get_template('search_nearby.html')
        self.response.write(template.render(template_value))

class Search(webapp2.RequestHandler):
    def get(self):
        start_id = self.request.get('start_id')
        if not start_id:
            start_id = 1
        keyword = self.request.get('keyword')
        requests = {'keyword':str(keyword)}
        headers = {"Content-type": "application/json", "Accept": "text/plain"}
        conn = httplib.HTTPConnection("the-city.appspot.com")
        conn.request("POST", "/api/search", json.dumps(requests), headers)
        responses = conn.getresponse()
        data = json.loads(responses.read())
        
        ##ongoing_title = list()
        ##ongoing_cover = list()
        ##ongoing_location = list()
        ##ongoing_holder = list()
        ##ongoing_take = list()
        ##ongoing_like = list()
        ##ongoing_start = list()
        ##ongoing_end = list()
        ##ongoing_act = list()
        ##ongoing_tag = list()

        ##past_title = list()
        ##past_cover = list()
        ##past_location = list()
        ##past_holder = list()
        ##past_take = list()
        ##past_like = list()
        ##past_start = list()
        ##past_end = list()
        ##past_act = list()
        ##past_tag = list()

        ##time = datetime.now()
        ##i = 0
        ##for start in start_time:
        ##    if start <= time:
        ##        past_title.append(title[i])
        ##        past_cover.append(cover[i])
        ##        past_location.append(location[i])
        ##        past_holder.append(holder[i])
        ##        past_take.append(take_number[i])
        ##        past_like.append(like_number[i])
        ##        past_start.append(start_time[i])
        ##        past_end.append(end_time[i])
        ##        past_act.append(act[i])
        ##        past_tag.append(tag[i])
        ##    else:
        ##        ongoing_title.append(title[i])
        ##        ongoing_cover.append(cover[i])
        ##        ongoing_location.append(location[i])
        ##        ongoing_holder.append(holder[i])
        ##        ongoing_take.append(take_number[i])
        ##        ongoing_like.append(like_number[i])
        ##        ongoing_start.append(start_time[i])
        ##        ongoing_end.append(end_time[i])
        ##        ongoing_act.append(act[i])
        ##        ongoing_tag.append(tag[i])
        ##    i = i+1
        past_next = 0
        ongoing_next = 0
        past_count = len(data['past_title'])-(int(start_id)-1)*5
        if past_count - 5 > 0:
            past_count = 5
            past_next = 1
        ongoing_count = len(data['ongoing_title'])-(int(start_id)-1)*5
        if ongoing_count - 5 > 0:
            ongoing_count = 5
            ongoing_next = 1
        print "hahahaha"
        print ongoing_count
        print past_count
        template_value = dict()
        template_value={
                'start_id':int(start_id),
                'past_next':int(past_next),
                'ongoing_next': int(ongoing_next),
                'keyword':keyword,
                'past_count':past_count,
                'ongoing_count':ongoing_count,
                'past_act':     data['past_activity'],
                'past_title':   data['past_title'],
                'past_cover':   data['past_cover'],
                'past_location':data['past_location'],
                'past_holder':   data['past_holder'],
                'past_take':    data['past_take_number'],
                'past_like':    data['past_like_number'],
                'past_start':   data['past_start_time'],
                'past_end':     data['past_end_time'],
                'past_tag':     data['past_tag'],
                'past_holder_id': data['past_holder_id'],
                'ongoing_act':     data['ongoing_activity'],
                'ongoing_title':   data['ongoing_title'],
                'ongoing_cover':   data['ongoing_cover'],
                'ongoing_location':data['ongoing_location'],
                'ongoing_holder':   data['ongoing_holder'],
                'ongoing_take':    data['ongoing_take_number'],
                'ongoing_like':    data['ongoing_like_number'],
                'ongoing_start':   data['ongoing_start_time'],
                'ongoing_end':     data['ongoing_end_time'],
                'ongoing_tag':     data['ongoing_tag'],
                'ongoing_holder_id': data['ongoing_holder_id'],
                }
	template = JINJA_ENVIRONMENT.get_template('search.html')
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
        (decorator.callback_path, decorator.callback_handler()),
	('/image_upload', Image_Upload),
	('/search_nearby', Search_nearby),
        ('/search',Search),
], debug = True)
















