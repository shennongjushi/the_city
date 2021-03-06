import cgi
import urllib
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import images
import webapp2
import json
import base64
import os
import pickle
import logging
import httplib2
import math
from apiclient import discovery
from oauth2client import appengine
from oauth2client import client
from google.appengine.api import memcache
from datetime import *
from gcm import *
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

# Images under an Activity, its parent is an activity
class Imag(ndb.Model):
    url = ndb.StringProperty()
    blob_key = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add = True)

# Greeting to person
class Greeting_person(ndb.Model):
    author = ndb.StringProperty()
    content = ndb.StringProperty(indexed = False)
    date = ndb.DateTimeProperty(auto_now_add=True)

class Activity_comment(ndb.Model):
    author = ndb.StringProperty()
    content = ndb.StringProperty(indexed = False)
    date = ndb.DateTimeProperty(auto_now_add = True)
# Activity
class Activity(ndb.Model):
    # Content of the Activity
    title = ndb.StringProperty()#Activity title
    start_date = ndb.DateTimeProperty()#Start date
    end_date = ndb.DateTimeProperty()#End date
    neighborhood = ndb.StringProperty()
    zipcode = ndb.StringProperty()
    address = ndb.StringProperty()#Location of the activity
    latitude = ndb.StringProperty()#For google map
    longitude = ndb.StringProperty()#For google map
    host = ndb.StringProperty()#The name of the host
    tag = ndb.StringProperty()#The type of the activity
    details = ndb.StringProperty(indexed = False) # The details of the activity
    # others
    like_number = ndb.IntegerProperty()
    take_number = ndb.IntegerProperty()
    hot_number = ndb.IntegerProperty()
    date = ndb.DateTimeProperty(auto_now_add = True)#The create date
    cover = ndb.StringProperty()#Blobstore key

class Webusers(ndb.Model):#Each Webusers xx.key.id() is the user
    nickname = ndb.StringProperty()
    gender = ndb.StringProperty()
    birthday = ndb.DateTimeProperty()
    my_activity = ndb.StringProperty(repeated = True) #The id of the activity I post
    like_activity = ndb.StringProperty(repeated = True)#The id of the activity I like
    #want_take_activity = ndb.StringProperty(repeated = True)#The id of the activity I want to take
    take_activity = ndb.StringProperty(repeated = True)#The id of the activity I have taken
    photo = ndb.StringProperty()
    subscribe = ndb.StringProperty(repeated = True)
    interest = ndb.StringProperty(repeated = True)
    introduce = ndb.StringProperty(indexed = False)
    google_calendar = ndb.BooleanProperty()
    calendar_key = ndb.StringProperty(repeated = True)
    device_key = ndb.StringProperty(repeated = True)
    device_on = ndb.BooleanProperty()

##Change time format for google calendar
def change_time_format(time, time_type):
    t = time + timedelta(hours = 6)
    year = t.year
    month = t.month
    day = t.day
    hour = t.hour
    minute = t.minute
    if month < 10:
	month = '0'+str(month)
    else:
	month = str(month)
    if day < 10:
	day = '0'+ str(day)
    else:
	day = str(day)
    if hour < 10:
	hour = '0' + str(hour)
    else:
	hour = str(hour)
    if minute < 10:
	minute = '0' + str(minute)
    else:
	minute = str(minute)
    if time_type == 0:
        return str(year)+month+day+'T'+hour+minute+'00Z' 
    else:
	return str(year)+'-'+month+'-'+day+'T'+hour+':'+minute+':00-00:00'


#Post activity upload to blobstore and database
class Upload_api(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
	print "hehe"
	new_host = self.request.get('user')
	user = ndb.Key(Webusers, new_host).get()
	if user:
	    new_tag = self.request.get('tag')
	    new_title = self.request.get('title')
	    new_start_date = self.request.get('start_date')
	    new_end_date = self.request.get('end_date')
	    new_neighborhood = self.request.get('neighborhoods')
 	    new_zipcode = self.request.get('zipcode')
	    new_address = self.request.get('address')
	    new_details= self.request.get('details')
	    new_latitude = self.request.get('latitude')
	    new_longitude = self.request.get('longitude')
	    new_cover = self.get_uploads('cover')
	    if new_cover:
	        blob_info = new_cover[0]
	        blob_key = str(blob_info.key())
	    else:
	        blob_key = ''
	    print "hello"
	    print blob_key
	    new_start_date = datetime(int(new_start_date[0:4]), int(new_start_date[5:7]), int(new_start_date[8:10]), int(new_start_date[11:13]), int(new_start_date[14:16]))
	    new_end_date = datetime(int(new_end_date[0:4]), int(new_end_date[5:7]), int(new_end_date[8:10]), int(new_end_date[11:13]), int(new_end_date[14:16]))
	    #activity	
	    activity = Activity(title = new_title, tag = new_tag, neighborhood =
                    new_neighborhood, zipcode = new_zipcode, address =
                    new_address, latitude = new_latitude, longitude =
                    new_longitude, host = new_host, cover = blob_key, start_date
                    = new_start_date, end_date = new_end_date, details =
                    new_details, like_number = 0, take_number = 0,hot_number = 0)
	    activity_key = activity.put()
	    #user
	    user.my_activity.append(str(activity_key.id()))
	    user.put()
	    self.redirect('/my_city')
	    

class Profile_api(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
	user_ = self.request.get('user')
	user_query = ndb.Key(Webusers, str(user_)).get()
	if not user_query:
	    user_query = Webusers(id=str(user_))
	    user_query.google_calendar = False
	    user_query.device_on = False
	user_query.nickname = self.request.get('nick')
	user_query.gender = self.request.get('gender')
	birthday_ = self.request.get('birthday')
	if birthday_:
	    user_query.birthday = datetime(int(birthday_[0:4]),int(birthday_[5:7]),int(birthday_[8:10]))
	user_query.introduce = self.request.get('introduce')
	#interest
	if user_query.interest:
	    user_query.interest = []
	for item in self.request.get_all('interest'):
	    user_query.interest.append(str(item))
	photo = self.get_uploads('photo')
	if photo:
	    if user_query.photo:
                blobstore.delete(urllib.unquote(user_query.photo))
	    blob_info = photo[0]
	    user_query.photo = str(blob_info.key())
	user_query.put()
	self.redirect('/my_city') 

class Person_api(webapp2.RequestHandler):
    def post(self):
	requests = json.loads(self.request.body)
        user_id = requests['user_id']
	user = ndb.Key(Webusers, str(user_id)).get()
	if not user:
	    user = Webusers(id=str(user_id))
	    user.google_calendar = False
	    user.device_on = False
	    user.put()
	users = Webusers.query().fetch()
	subscribe_me_id = list()
	for each in users:
	    if user_id in each.subscribe:
		subscribe_me_id.append(each.key.id())
	responses = {
	    'taken': user.take_activity,
	    'like': user.like_activity,
	    'post': user.my_activity,
	    'nick': user.nickname,
	    'introduce':user.introduce,
	    'interest':user.interest,
	    'photo':user.photo,
	    'sub_me': subscribe_me_id,
	    'i_sub': user.subscribe,
	    'gender':user.gender,
	}
        self.response.headers['Content-Type'] = "application/json"
        self.response.headers['Accept'] = "text/plain"
        self.response.write(json.dumps(responses))

class Greeting_person_api(webapp2.RequestHandler):
    def post(self):
	user = self.request.get('user')
	guest = self.request.get('guest')
	if user:
	    greeting = Greeting_person(parent = ndb.Key(Webusers, str(user)))
	    if guest:
		guest_query = ndb.Key(Webusers,str(guest)).get()
		if guest_query:
	            greeting.author = guest_query.nickname
	    greeting.content = self.request.get('content')
	    greeting.put()
	    self.redirect('/person?user=%s' %user)
 
class Activity_comment_api(webapp2.RequestHandler):
    def post(self):
	requests = json.loads(self.request.body)
	activity_id = requests['activity_id']
	guest_id = requests['guest_id']
	comment = requests['comment']
	author = ''
	activity = ndb.Key(Activity, long(activity_id)).get()
	if activity:
	    comment_entity = Activity_comment(parent = ndb.Key(Activity, long(activity_id)))
	    if guest_id:
	        guest_query = ndb.Key(Webusers, str(guest_id)).get()
	    	if guest_query:
		    comment_entity.author = guest_query.nickname
		    author = guest_query.nickname
	    comment_entity.content = comment
	    comment_entity.put()
	responses = {
	    'author':author,
	    'content':comment
	}
        self.response.headers['Content-Type'] = "application/json"
        self.response.headers['Accept'] = "text/plain"
        self.response.write(json.dumps(responses))
 
class Subscribe_api(webapp2.RequestHandler):
    def post(self):
	user_id = self.request.get('user')
	guest_id = self.request.get('guest')
	action = self.request.get('action')
	guest = ndb.Key(Webusers, str(guest_id)).get()
	if user_id not in guest.subscribe and action == 'subscribe':
	    guest.subscribe.append(str(user_id))
	    guest.put()
	####### For gcm ########
	    user_query = ndb.Key(Webusers,str(user_id)).get()
	    if user_query:
	        if user_query.device_on:
	            for key in user_query.device_key:
			try:
                            gcm = GCM("AIzaSyAje3whZxvNCwZ5uejwQG4VFsrr01jb3MM")
			    data = {'guest': guest.nickname,'user':user_query.nickname}
                            gcm.plaintext_request(registration_id=str(key), data=data)
			except:
			    print "not valid"
            #            # Plaintext request
	        #gcm = GCM("AIzaSyAje3whZxvNCwZ5uejwQG4VFsrr01jb3MM")
	        #data = {'param1': 'value1', 'param2': 'value2'}
	    
	        ## Plaintext request
	        #reg_id = "APA91bG5EhT0wiMXu0OE3g6p6tefMP-P52Hi4tyexvrQBXX5AlorpO8z5tbTwOCZhyxWgrbURk2anbMsntnFtWlCCDbGXUg9siu12BQXD_c3Qxg45pO6o2KHLqrBq_StVj5OPhtWkzQ5vhuGrkSEPlGj8p4vb6atLnzNXCeJ4_K2k_0uT4YmqdI"
	        #gcm.plaintext_request(registration_id=reg_id, data=data)

	####### For gcm ########
	if user_id in guest.subscribe and action == 'unsubscribe':
	    guest.subscribe.remove(str(user_id))
	    guest.put()
	self.redirect('/person?user=%s' %user_id)
	   
class Activity_api(webapp2.RequestHandler):
    def post(self):
	requests = json.loads(self.request.body)
	activity_id = requests['activity_id']
	guest_id = requests['guest_id']
	activity = ndb.Key(Activity, long(activity_id)).get()
	if activity:
	    start_date = str(activity.start_date.year)+'/'+str(activity.start_date.month)+'/'+str(activity.start_date.day)+ ' '+ str(activity.start_date.hour)+':'+str(activity.start_date.minute)
	    end_date = str(activity.end_date.year)+'/'+str(activity.end_date.month)+'/'+str(activity.end_date.day)+ ' '+ str(activity.end_date.hour)+':'+str(activity.end_date.minute)
	    date = str(activity.date.year)+'/'+str(activity.date.month)+'/'+str(activity.date.day)+ ' '+ str(activity.date.hour)+':'+str(activity.date.minute)
	    host = ndb.Key(Webusers, str(activity.host)).get()
	    host_photo = ''
	    host_nick = ''
	    take_action = 1
	    like_action = 1
	    guest = ''
	    if guest_id:
	        guest = ndb.Key(Webusers, str(guest_id)).get()
	    if guest:
	       if activity_id in guest.take_activity:
	           take_action = 0
	       if activity_id in guest.like_activity:
	           like_action = 0
	    all_date = list()
	    if activity.end_date:
		start = datetime(activity.start_date.year,activity.start_date.month,activity.start_date.day)
		end = datetime(activity.end_date.year, activity.end_date.month, activity.end_date.day)
		delta = end - start
		for i in range(delta.days+1):
		    item = start + timedelta(days = i)
		    all_date.append(str(item.year)+'/'+str(item.month)+'/'+str(item.day))
	    if host:
		host_photo = host.photo
		host_nick = host.nickname
	   #######Google Calendar date calculate#########
	    calendar_start = ''
	    calendar_end = ''
	    if activity.start_date:
		calendar_start = change_time_format(activity.start_date,0)
		
	    if activity.end_date:
		calendar_end = change_time_format(activity.end_date,0)
	   #################### Imag #################### 
	    images = Imag.query(ancestor = ndb.Key(Activity, long(activity_id))).order(Imag.date).fetch()
	    image_urls = list()
	    for image in images:
	        image_urls.append(image.url)
	    responses = {
		'title':activity.title,
		'start_date':start_date,
		'end_date':end_date,
		'neighborhood':activity.neighborhood,
		'zipcode':activity.zipcode,
		'address':activity.address,
		'latitude':activity.latitude,
		'longitude':activity.longitude,
		'host':activity.host,
		'tag':activity.tag,
		'details':activity.details,
		'like_number':activity.like_number,
		'take_number':activity.take_number,
		'cover':activity.cover,
		'date':date,
		'host_photo':host_photo,
		'host_nick':host_nick,
		'all_date':all_date,
		'like_action':like_action,
		'take_action':take_action,
		'calendar_start':calendar_start,
		'calendar_end':calendar_end,
		'pics':image_urls
	    }	
            self.response.headers['Content-Type'] = "application/json"
            self.response.headers['Accept'] = "text/plain"
            self.response.write(json.dumps(responses))
 
class Like_api(webapp2.RequestHandler):
    def post(self):
	requests = json.loads(self.request.body)
	activity_id = requests['activity_id']
        guest_id = requests['guest_id']
	action = requests['action']
	activity = ndb.Key(Activity, long(activity_id)).get()
	guest = ndb.Key(Webusers, str(guest_id)).get()
	like_number = activity.like_number
	if action == "1" and (str(activity_id) not in guest.like_activity):
	    like_number = activity.like_number + 1
	    activity.like_number = activity.like_number + 1
            activity.hot_number = activity.hot_number + 1
	    activity.put()
	    guest.like_activity.append(str(activity_id))
	    guest.put()
	    action = "0"
	elif action == "0" and (str(activity_id) in guest.like_activity):
	    like_number = activity.like_number - 1
	    activity.like_number = activity.like_number - 1
            activity.hot_number = activity.hot_number -1
	    activity.put()
	    guest.like_activity.remove(str(activity_id))
	    guest.put()
	    action = "1" 
	responses = {
	    'like':str(like_number),
	    'action':action
	}
        self.response.headers['Content-Type'] = "application/json"
        self.response.headers['Accept'] = "text/plain"
        self.response.write(json.dumps(responses))

class Android_Take(webapp2.RequestHandler):
    def post(self):
	requests = json.loads(self.request.body)
	activity_id = requests['activity_id']
        guest_id = requests['guest_id']
	action = requests['action']
	activity = ndb.Key(Activity, long(activity_id)).get()
	guest = ndb.Key(Webusers, str(guest_id)).get()
	take_number = activity.take_number
	if action == "1" and (str(activity_id) not in guest.take_activity):
	    take_number = activity.take_number + 1
	    activity.take_number = activity.take_number + 1
            activity.hot_number = activity.hot_number + 1
	    activity.put()
	    guest.take_activity.append(str(activity_id))
	    guest.put()
	    action = "0"
	elif action == "0" and (str(activity_id) in guest.take_activity):
	    take_number = activity.take_number - 1
	    activity.take_number = activity.take_number - 1
            activity.hot_number = activity.hot_number -1
	    activity.put()
	    guest.take_activity.remove(str(activity_id))
	    guest.put()
	    action = "1" 
	responses = {
	    'action':action
	}
        self.response.headers['Content-Type'] = "application/json"
        self.response.headers['Accept'] = "text/plain"
        self.response.write(json.dumps(responses))

class Take_api(webapp2.RequestHandler):
    @decorator.oauth_aware
    def post(self):
	requests = json.loads(self.request.body)
	activity_id = requests['activity_id']
	guest_id = requests['guest_id']
	action = requests['action']
	comment = requests['comment']
	author = ''
	activity_key = ndb.Key(Activity, long(activity_id))
	activity = activity_key.get()
	if activity and action == '1' and comment:
	    comment_entity = Activity_comment(parent = ndb.Key(Activity, long(activity_id)))
	    if guest_id:
	        guest_query = ndb.Key(Webusers, str(guest_id)).get()
	    	if guest_query:
		    comment_entity.author = guest_query.nickname
		    author = guest_query.nickname
	    comment_entity.content = comment
	    comment_entity.put()
	guest = ndb.Key(Webusers, str(guest_id)).get()
	take_number = activity.take_number
	if action == "1" and (str(activity_id) not in guest.take_activity):
	    take_number = activity.take_number + 1
	    activity.take_number = activity.take_number + 1
            activity.hot_number = activity.hot_number + 1
	    activity.put()
	    guest.take_activity.append(str(activity_id))
	    if decorator.has_credentials():
		guest.google_calendar = True 
	    guest.put()
	    action = "0"
	elif action == "0" and (str(activity_id) in guest.take_activity):
	    take_number = activity.take_number - 1
	    activity.take_number = activity.take_number - 1
            activity.hot_number = activity.hot_number - 1
	    activity.put()
	    guest.take_activity.remove(str(activity_id))
	    if decorator.has_credentials():
		guest.google_calendar = True
	    guest.put()
	    action = "1"
	responses = {
	    'take': str(take_number),
	    'action': action,
	    'author':author,
	    'content':comment
	}
#####################################################
#		Google Calendar
#####################################################
	calendar_start = ''
	calendar_end = ''
	if activity.start_date:
	    calendar_start = change_time_format(activity.start_date,1) 
	if activity.end_date:
	    calendar_end = change_time_format(activity.end_date,1)
	if decorator.has_credentials() and requests['action'] == '1':
    	     event = {
    	       'summary':activity.title,
    	       'location': activity.address,
    	       'start': {
    		'dateTime': calendar_start
    	     	},
    	       'end': {
    		'dateTime': calendar_end
    	        },
    	     }
    	     http = decorator.http()
    	     created_event = service.events().insert(calendarId='primary', body=event).execute(http)
	     guest.calendar_key.append(str(activity_id)+':'+created_event['id'])
	     guest.put()
	elif decorator.has_credentials() and requests['action'] == "0":
	     for key in guest.calendar_key:
		if str(activity_id) in key:
		    event = key.split(':')
    	     	    http = decorator.http()
		    delete_event = service.events().delete(calendarId='primary', eventId=str(event[1])).execute(http)
		    guest.calendar_key.remove(key)
		    break
#####################################################
#		Google Calendar
#####################################################
	print "take number= " + str(take_number)
        self.response.headers['Content-Type'] = "application/json"
        self.response.headers['Accept'] = "text/plain"
        self.response.write(json.dumps(responses))

class Image_upload_api(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
	activity_id = self.request.get('activity_id')
	activity = ndb.Key(Activity, long(activity_id)).get()	
	image = self.get_uploads('image')
	if image and activity:
	    blob_info = image[0]
	    image_new = Imag(parent=ndb.Key(Activity, long(activity_id)))
	    image_new.blob_key = str(blob_info.key())
	    image_new.url = '/img?key='+str(blob_info.key())
	    image_new.put()
	self.redirect('/image_upload?finish=1')

class Get_all_api(webapp2.RequestHandler):
    def post(self):
        activities = Activity.query().order(Activity.start_date).fetch()
        responses = dict()
        responses['ongoing_title'] = list()
        responses['ongoing_cover'] = list()
        responses['ongoing_location'] = list()
        responses['ongoing_holder'] = list()
        responses['ongoing_holder_id'] = list()
        responses['ongoing_take_number'] = list()
        responses['ongoing_like_number'] = list()
        responses['ongoing_start_time'] = list()
        responses['ongoing_end_time'] = list()
        responses['ongoing_activity'] = list()
        responses['ongoing_tag'] = list()
        responses['past_title'] = list()
        responses['past_cover'] = list()
        responses['past_location'] = list()
        responses['past_holder'] = list()
        responses['past_holder_id'] = list()
        responses['past_take_number'] = list()
        responses['past_like_number'] = list()
        responses['past_start_time'] = list()
        responses['past_end_time'] = list()
        responses['past_activity'] = list()
        responses['past_tag'] = list()
        time = datetime.now()
        for activity in activities:
            if activity.end_date < time:
                responses['past_activity'].append(activity.key.id())
                responses['past_title'].append(activity.title)
                responses['past_cover'].append(activity.cover)
                responses['past_location'].append(activity.address)
	        host = ndb.Key(Webusers, str(activity.host)).get()
                responses['past_holder'].append(host.nickname)
                responses['past_holder_id'].append(host.key.id())
                responses['past_start_time'].append( str(activity.start_date.year)+'/'+str(activity.start_date.month)+'/'+str(activity.start_date.day)+ ' '+ str(activity.start_date.hour)+':'+str(activity.start_date.minute))
                responses['past_end_time'].append(str(activity.end_date.year)+'/'+str(activity.end_date.month)+'/'+str(activity.end_date.day)+ ' '+ str(activity.end_date.hour)+':'+str(activity.end_date.minute))
                responses['past_take_number'].append(activity.take_number)
                responses['past_like_number'].append(activity.like_number)
                responses['past_tag'].append(activity.tag)
            else:
                responses['ongoing_activity'].append(activity.key.id())
                responses['ongoing_title'].append(activity.title)
                responses['ongoing_cover'].append(activity.cover)
                responses['ongoing_location'].append(activity.address)
	        host = ndb.Key(Webusers, str(activity.host)).get()
                responses['ongoing_holder'].append(host.nickname)
                responses['ongoing_holder_id'].append(host.key.id())
                responses['ongoing_start_time'].append( str(activity.start_date.year)+'/'+str(activity.start_date.month)+'/'+str(activity.start_date.day)+ ' '+ str(activity.start_date.hour)+':'+str(activity.start_date.minute))
                responses['ongoing_end_time'].append(str(activity.end_date.year)+'/'+str(activity.end_date.month)+'/'+str(activity.end_date.day)+ ' '+ str(activity.end_date.hour)+':'+str(activity.end_date.minute))
                responses['ongoing_take_number'].append(activity.take_number)
                responses['ongoing_like_number'].append(activity.like_number)
                responses['ongoing_tag'].append(activity.tag)
        self.response.headers['Content-Type'] = "application/json"
        self.response.headers['Accept'] = "text/plain"
        self.response.write(json.dumps(responses))

class Search_api(webapp2.RequestHandler):
    def post(self):
        requests = json.loads(self.request.body)
        query_string = str(requests['keyword'])
        print"aaaaaaaaaaaaaa"
        activities = Activity.query().order(Activity.start_date).fetch()
        responses = dict()
        responses['ongoing_title'] = list()
        responses['ongoing_cover'] = list()
        responses['ongoing_location'] = list()
        responses['ongoing_holder'] = list()
        responses['ongoing_holder_id'] = list()
        responses['ongoing_take_number'] = list()
        responses['ongoing_like_number'] = list()
        responses['ongoing_start_time'] = list()
        responses['ongoing_end_time'] = list()
        responses['ongoing_activity'] = list()
        responses['ongoing_tag'] = list()
        responses['past_title'] = list()
        responses['past_cover'] = list()
        responses['past_location'] = list()
        responses['past_holder'] = list()
        responses['past_holder_id'] = list()
        responses['past_take_number'] = list()
        responses['past_like_number'] = list()
        responses['past_start_time'] = list()
        responses['past_end_time'] = list()
        responses['past_activity'] = list()
        responses['past_tag'] = list()
        time = datetime.now()
        for activity in activities:
            if query_string.lower() in activity.title.lower():
                if activity.end_date < time:
                    responses['past_activity'].append(activity.key.id())
                    responses['past_title'].append(activity.title)
                    responses['past_cover'].append(activity.cover)
                    responses['past_location'].append(activity.address)
	            host = ndb.Key(Webusers, str(activity.host)).get()
                    responses['past_holder'].append(host.nickname)
                    responses['past_holder_id'].append(host.key.id())
                    responses['past_start_time'].append( str(activity.start_date.year)+'/'+str(activity.start_date.month)+'/'+str(activity.start_date.day)+ ' '+ str(activity.start_date.hour)+':'+str(activity.start_date.minute))
                    responses['past_end_time'].append(str(activity.end_date.year)+'/'+str(activity.end_date.month)+'/'+str(activity.end_date.day)+ ' '+ str(activity.end_date.hour)+':'+str(activity.end_date.minute))
                    responses['past_take_number'].append(activity.take_number)
                    responses['past_like_number'].append(activity.like_number)
                    responses['past_tag'].append(activity.tag)
                else:
                    responses['ongoing_activity'].append(activity.key.id())
                    responses['ongoing_title'].append(activity.title)
                    responses['ongoing_cover'].append(activity.cover)
                    responses['ongoing_location'].append(activity.address)
	            host = ndb.Key(Webusers, str(activity.host)).get()
                    responses['ongoing_holder'].append(host.nickname)
                    responses['ongoing_holder_id'].append(host.key.id())
                    responses['ongoing_start_time'].append( str(activity.start_date.year)+'/'+str(activity.start_date.month)+'/'+str(activity.start_date.day)+ ' '+ str(activity.start_date.hour)+':'+str(activity.start_date.minute))
                    responses['ongoing_end_time'].append(str(activity.end_date.year)+'/'+str(activity.end_date.month)+'/'+str(activity.end_date.day)+ ' '+ str(activity.end_date.hour)+':'+str(activity.end_date.minute))
                    responses['ongoing_take_number'].append(activity.take_number)
                    responses['ongoing_like_number'].append(activity.like_number)
                    responses['ongoing_tag'].append(activity.tag)

            elif query_string.lower() in activity.address.lower():
                if activity.end_date < time:
                    responses['past_activity'].append(activity.key.id())
                    responses['past_title'].append(activity.title)
                    responses['past_cover'].append(activity.cover)
                    responses['past_location'].append(activity.address)
	            host = ndb.Key(Webusers, str(activity.host)).get()
                    responses['past_holder'].append(host.nickname)
                    responses['past_holder_id'].append(host.key.id())
                    responses['past_start_time'].append( str(activity.start_date.year)+'/'+str(activity.start_date.month)+'/'+str(activity.start_date.day)+ ' '+ str(activity.start_date.hour)+':'+str(activity.start_date.minute))
                    responses['past_end_time'].append(str(activity.end_date.year)+'/'+str(activity.end_date.month)+'/'+str(activity.end_date.day)+ ' '+ str(activity.end_date.hour)+':'+str(activity.end_date.minute))
                    responses['past_take_number'].append(activity.take_number)
                    responses['past_like_number'].append(activity.like_number)
                    responses['past_tag'].append(activity.tag)
                else:
                    responses['ongoing_activity'].append(activity.key.id())
                    responses['ongoing_title'].append(activity.title)
                    responses['ongoing_cover'].append(activity.cover)
                    responses['ongoing_location'].append(activity.address)
	            host = ndb.Key(Webusers, str(activity.host)).get()
                    responses['ongoing_holder'].append(host.nickname)
                    responses['ongoing_holder_id'].append(host.key.id())
                    responses['ongoing_start_time'].append( str(activity.start_date.year)+'/'+str(activity.start_date.month)+'/'+str(activity.start_date.day)+ ' '+ str(activity.start_date.hour)+':'+str(activity.start_date.minute))
                    responses['ongoing_end_time'].append(str(activity.end_date.year)+'/'+str(activity.end_date.month)+'/'+str(activity.end_date.day)+ ' '+ str(activity.end_date.hour)+':'+str(activity.end_date.minute))
                    responses['ongoing_take_number'].append(activity.take_number)
                    responses['ongoing_like_number'].append(activity.like_number)
                    responses['ongoing_tag'].append(activity.tag)
        print responses
        self.response.headers['Content-Type'] = "application/json"
        self.response.headers['Accept'] = "text/plain"
        self.response.write(json.dumps(responses))


############### Search Nearby ##################
def distance(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination
    #radius = 6371 # km
    radius = 3958.75 #mi
    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = round(radius * c,4)
    return d

class Nearby(webapp2.RequestHandler):
    def post(self):
	requests = json.loads(self.request.body)
	request_radius = requests['radius']
	latitude = requests['latitude']
	longitude = requests['longitude']
        activity_all = Activity.query(ndb.AND(Activity.latitude!=None, Activity.latitude!="")).fetch()
  	activity_all = sorted(activity_all,key=lambda activity: distance((float(activity.latitude),float(activity.longitude)),(float(latitude),float(longitude))))
	if request_radius:
 	    search_result = [activity for activity in activity_all if distance((float(activity.latitude),float(activity.longitude)),(float(latitude),float(longitude))) < float(request_radius)]
	else:
	    search_result = activity_all
	result=dict()
	result['markers']=list()
	for i in range(len(search_result)):
	    marker = dict()
	    marker['title'] = search_result[i].title
	    marker['activity'] = search_result[i].key.id()
	    marker['cover'] = search_result[i].cover
	    marker['latitude'] = search_result[i].latitude
	    marker['longitude'] = search_result[i].longitude
	    result['markers'].append(marker)
        self.response.headers['Content-Type'] = "application/json"
        self.response.headers['Accept'] = "text/plain"
        self.response.write(json.dumps(result))


class Hot_api(webapp2.RequestHandler):
    def post(self):
	result = dict()
        activity_query = Activity.query().order(-Activity.hot_number).fetch(10)
	result['hot_id'] = list()
	result['hot_title'] = list()
	result['hot_start'] = list()
	result['hot_end'] = list()
	result['hot_take'] = list()
	result['hot_like'] = list()
	result['hot_address'] = list()
	result['hot_type'] = list()
	result['hot_cover']=list()
	for activity in activity_query:
	    if activity.end_date > datetime.now():
	        result['hot_id'].append(str(activity.key.id()))
	        result['hot_title'].append(str(activity.title))
	        result['hot_start'].append(str(activity.start_date.year)+'/'+str(activity.start_date.month)+'/'+str(activity.start_date.day)+' '+str(activity.start_date.hour)+':'+str(activity.start_date.minute))
	        result['hot_end'].append(str(activity.end_date.year)+'/'+str(activity.end_date.month)+'/'+str(activity.end_date.day)+' '+str(activity.end_date.hour)+':'+str(activity.end_date.minute))
	        result['hot_take'].append(str(activity.take_number))
	        result['hot_like'].append(str(activity.like_number))
	        result['hot_address'].append(str(activity.address))
	        result['hot_type'].append(str(activity.tag))
	        result['hot_cover'].append(str(activity.cover))
	        print str(activity.key.id())
        self.response.headers['Content-Type'] = "application/json"
        self.response.headers['Accept'] = "text/plain"
        self.response.write(json.dumps(result))

class Android_get_upload_url(webapp2.RequestHandler):
    def post(self):
        requests = json.loads(self.request.body)
        activity_id = str(requests['activity_id'])
	responses = dict()
        responses['upload_url'] = blobstore.create_upload_url('/api/android_image_add?activity_id=%s' %(activity_id))
        self.response.headers['Content-Type'] = "application/json"
        self.response.headers['Accept'] = "text/plain"
        self.response.write(json.dumps(responses))

class Android_Image_Add(blobstore_handlers.BlobstoreUploadHandler):
   def post(self):
	activity_id = self.request.get('activity_id')
	activity = ndb.Key(Activity, long(activity_id)).get()	
	image = self.get_uploads('image')
	if image and activity:
	    blob_info = image[0]
	    image_new = Imag(parent=ndb.Key(Activity, long(activity_id)))
	    image_new.blob_key = str(blob_info.key())
	    image_new.url = '/img?key='+str(blob_info.key())
	    image_url = image_new.url
	    image_new.put()
	    self.response.write(image_url)
	else:
            self.response.write("")

class Gcm_id(webapp2.RequestHandler):
    def post(self):
	requests = json.loads(self.request.body)
	user_id = requests['email']
	reg_id = requests['reg_id']
	user_query = ndb.Key(Webusers, str(user_id)).get()
	if not user_query:
	    user_query = Webusers(id=str(user_id))
	    user_query.google_calendar = False
	    user_query.device_on = False
	if reg_id:
	    if str(reg_id) not in user_query.device_key:
		user_query.device_key.append(str(reg_id))
	user_query.put()
	responses = dict()
        self.response.headers['Content-Type'] = "application/json"
        self.response.headers['Accept'] = "text/plain"
        self.response.write(json.dumps(responses))
	
class Notification(webapp2.RequestHandler):
    def post(self):
	requests = json.loads(self.request.body)
	user_id = requests['email']
	action = requests['action']
	user = ndb.Key(Webusers, str(user_id)).get()
	if not user:
	    user = Webusers(id=str(user_id))
	    user.google_calendar = False
	    user.device_on = False
	    user.put()
	user = ndb.Key(Webusers,str(user_id)).get()
	status = ""
	if not user.device_on:
	    if action == "1":
	        user.device_on = True
		user.put()
	        status = "on"
	    else:
		status = "off"
	else:
	    if action == "1":
		user.device_on = False
		user.put()
		status = "off"
	    else:
	        status = "on"
	responses = {'status':status}
        self.response.headers['Content-Type'] = "application/json"
        self.response.headers['Accept'] = "text/plain"
        self.response.write(json.dumps(responses))
	
	
	
class Android_person_activity(webapp2.RequestHandler):
    def post(self):
	requests = json.loads(self.request.body)
	user_id = requests['email']
	action = requests['action']
	user = ndb.Key(Webusers, str(user_id)).get()
	if not user:
	    user = Webusers(id=str(user_id))
	    user.google_calendar = False
	    user.device_on = False
	    user.put()
	responses = dict()
	responses['ids'] = list()
	responses['covers'] = list()
	responses['titles'] = list()
	responses['starts'] = list()
	responses['ends'] = list()
	responses['locations'] = list()
	responses['types'] = list()
	activities = list()
	if action == '0':#Like
	    activities = user.like_activity
	elif action == '1': #Take
	    activities = user.take_activity
	elif action == '2': # Post
	    activities = user.my_activity
	for activity in activities:
	    activity_entity = ndb.Key(Activity,long(activity)).get()
	    responses['ids'].append(activity)
	    responses['covers'].append(activity_entity.cover)
	    responses['titles'].append(activity_entity.title)
            responses['starts'].append( str(activity_entity.start_date.year)+'/'+str(activity_entity.start_date.month)+'/'+str(activity_entity.start_date.day)+ ' '+ str(activity_entity.start_date.hour)+':'+str(activity_entity.start_date.minute))
            responses['ends'].append( str(activity_entity.end_date.year)+'/'+str(activity_entity.end_date.month)+'/'+str(activity_entity.end_date.day)+ ' '+ str(activity_entity.end_date.hour)+':'+str(activity_entity.end_date.minute))
	    responses['locations'].append(activity_entity.address)
	    responses['types'].append(activity_entity.tag)
        self.response.headers['Content-Type'] = "application/json"
        self.response.headers['Accept'] = "text/plain"
        self.response.write(json.dumps(responses))

application = webapp2.WSGIApplication([
    ('/api/post',Upload_api),
    ('/api/profile',Profile_api),
    ('/api/person',Person_api),
    ('/api/greeting_person', Greeting_person_api),
    ('/api/subscribe', Subscribe_api),
    ('/api/activity', Activity_api),
    ('/api/like', Like_api),
    ('/api/take', Take_api),
    ('/api/activity_comment',Activity_comment_api),
    ('/api/image_upload', Image_upload_api),
    ('/api/nearby', Nearby),
    ('/api/search',Search_api),
    ('/api/get_all',Get_all_api),
    ('/api/hot_activity', Hot_api),
    ('/api/android_take',Android_Take),
    ('/api/android_image_add',Android_Image_Add),
    ('/api/android_get_url',Android_get_upload_url),
    ('/api/android_person_activity',Android_person_activity),
    ('/api/gcm_id',Gcm_id),
    ('/api/device',Notification),
], debug=True)







