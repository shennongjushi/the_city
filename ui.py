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

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class Index(webapp2.RequestHandler):
    def get(self):
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
		'logout_url':logout_url 
	        }
		template = JINJA_ENVIRONMENT.get_template('index.html')
		self.response.write(template.render(template_value))
	else:
	    login_url = users.create_login_url('/')
	    template_value = {
		'user': user,
		'login_url':login_url
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
	        greetings_author = data['greetings_author']
	        greetings_content = data['greetings_content']
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
		'greetings_author':greetings_author,
		'greetings_content':greetings_content,
		'greetings_number':len(greetings_author),
		'user': user.email(),
		'guest': user.email(),
		'greetings':greetings,
		'login_url':login_url
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
	        greetings_author = data['greetings_author']
	        greetings_content = data['greetings_content']
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
		'greetings_author':greetings_author,
		'greetings_content':greetings_content,
		'greetings_number':len(greetings_author),
		'user': user,
		'guest': guest_id,
		'greetings':greetings
	    }
	    template = JINJA_ENVIRONMENT.get_template('person.html')
	    self.response.write(template.render(template_value))

class Activity_page(webapp2.RequestHandler):
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
		    print user.nickname

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
		'all_guests':all_guests
	    }
	    print "like_action:" + str(data['like_action'])
	    template = JINJA_ENVIRONMENT.get_template('activity.html')
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
], debug = True)
















