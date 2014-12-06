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
from datetime import *

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
    details = ndb.StringProperty() # The details of the activity
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
    introduce = ndb.StringProperty() 

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
	    self.redirect('/post')
	    

class Profile_api(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
	user_ = self.request.get('user')
	user_query = ndb.Key(Webusers, str(user_)).get()
	if not user_query:
	    user_query = Webusers(id=str(user_))
	user_query.nickname = self.request.get('nick')
	user_query.gender = self.request.get('gender')
	birthday_ = self.request.get('birthday')
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
	users = Webusers.query().fetch()
	i = 0
	for each in users:
	    if user_id in each.subscribe:
		i = i + 1
	#greeting
	greetings_author = list()
	greetings_content = list()
	greetings = Greeting_person.query(ancestor=ndb.Key(Webusers, str(user_id))).order(Greeting_person.date).fetch()
	for greeting in greetings:
	    greetings_author.append(greeting.author)
	    greetings_content.append(greeting.content)
	responses = {
	    'taken': user.take_activity,
	    'like': user.like_activity,
	    'post': user.my_activity,
	    'nick': user.nickname,
	    'introduce':user.introduce,
	    'interest':user.interest,
	    'photo':user.photo,
	    'sub_me_number': i,
	    'gender':user.gender,
	    'greetings_author':greetings_author,
	    'greetings_content':greetings_content
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
	guest = ndb.Key(Webusers, str(guest_id)).get()
	guest.subscribe.append(str(user_id))
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

class Take_api(webapp2.RequestHandler):
    def post(self):
	requests = json.loads(self.request.body)
	activity_id = requests['activity_id']
	guest_id = requests['guest_id']
	action = requests['action']
	comment = requests['comment']
	author = ''
	activity = ndb.Key(Activity, long(activity_id)).get()
	if activity and action == '1':
	    comment_entity = Activity_comment(parent = ndb.Key(Activity, long(activity_id)))
	    if guest_id:
	        guest_query = ndb.Key(Webusers, str(guest_id)).get()
	    	if guest_query:
		    comment_entity.author = guest_query.nickname
		    author = guest_query.nickname
	    comment_entity.content = comment
	    comment_entity.put()
	guest = ndb.Key(Webusers, str(guest_id)).get()
	take_number = activity.like_number
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
            activity.hot_number = activity.hot_number - 1
	    activity.put()
	    guest.take_activity.remove(str(activity_id))
	    guest.put()
	    action = "1"
	responses = {
	    'take': str(take_number),
	    'action': action,
	    'author':author,
	    'content':comment
	}
	print "take number= " + str(take_number)
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
    ('/api/activity_comment',Activity_comment_api)
], debug=True)
