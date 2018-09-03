from fake_useragent import UserAgent
import requests
import hashlib
import os
import random
import string
import pickle
import time

URL_BASE     = "https://www.fxp.co.il/"
URL_REGISTER = URL_BASE + "register.php?do=addmember"
URL_REPLY    = URL_BASE + "newreply.php?do=postreply&t="
URL_THREAD   = URL_BASE + "newthread.php?do=postthread&f="

def string_to_hex(string):
	return '%'.join("{:02x}".format(ord(c)) for c in string)

def register(ses, email, username, password, useragent):
	print("Registering\nUser: {0}\nPass: {1}".format(username, password))
	password_md5 = hashlib.md5(password).hexdigest()
	header = {
		'User-Agent': useragent
	}
	data = {
		#dynamic
		'username': username,
		'password': password,
		'passwordconfirm': password,
		'email': email,
		'emailconfirm': email,
		'agree': "1",
		#hidden
		's': "",
		'securitytoken': "guest",
		'do': "addmember",
		'url': URL_BASE,
		'password_md5': password_md5,
		'passwordconfirm_md5': password_md5,
		'day': "",
		'month': "",
		'year': ""
	}

	res = ses.post(URL_REGISTER, headers=header, data=data)
	return res if "<strong>{0}</strong>".format(username) in res.text else None
	
def reply(ses, useragent, thread, message):
	target = URL_REPLY + thread
	header = {
		'User-Agent': useragent
	}
	
	res = ses.post(target, headers=header)
	token = res.text.split('<input type="hidden" name="securitytoken" value="')[1].split('"')[0]
	userid = res.text.split('var USER_ID_Forum = "')[1].split('"')[0]
	data = {
		'do': "postreply",
		's': "",
		'p': "",
		't': thread,
		'loggedinuser': userid,
		'poststarttime': str(int(time.time())-30),
		'securitytoken': token,
		'message_backup': message,
		'message': message,
		'wysiwyg': "1"
	}
	res = ses.post(target, cookies=ses.cookies, headers=header, data=data)
	return '<div class="blockrow error" id="qr_error_td"></div>' in res.text
	
def thread(ses, useragent, forum, title, message):
	target = URL_THREAD + forum
	print("Posting to "+str(forum))
	header = {
		'User-Agent': useragent
	}
	res = ses.post(target, headers=header)
	token = res.text.split('<input type="hidden" name="securitytoken" value="')[1].split('"')[0]
	userid = res.text.split('var USER_ID_Forum = "')[1].split('"')[0]
	data = {
		'do': "postthread",
		's': "",
		'p': "",
		'f': forum,
		'loggedinuser': userid,
		'poststarttime': "",
		'securitytoken': token,
		'subject': title,
		'message_backup': message,
		'message': message,
		'wysiwyg': "1"
	}
	res = ses.post(target, headers=header, data=data)
	return '<div class="blockrow error" id="qr_error_td"></div>' in res.text
	
class User(object):
	def __new__(cls, username, email=None):
		#hi, i want to access username
		file_path = "users/"+username
		#check if exists in db, if so, load instance
		if os.path.isfile(file_path):
			return pickle.load(open(file_path, 'r'))
			#return Forum(cookies, email, username, password, useragent)
		#doesnt exist in db! make sure theres an email
		if email is None:
			return None
		ses = requests.Session()
		email = email
		username = username
		password = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(random.randint(6,12)))
		useragent = UserAgent().random
		res = register(ses, email, username, password, useragent)
		#if cannot register return none
		if res is None:
			return None
		#didnt return, we have the cookies!
		userid = res.text.split('var USER_ID_Forum = "')[1].split('"')[0]
		#create instance
		ins = Forum(ses, email, username, password, useragent, userid)
		#dump it
		with open(file_path, "wb") as file_user:
			pickle.dump(ins, file_user)
		#return instance
		return ins

class Forum(object):
	def __init__(self, ses, email, username, password, useragent, userid):
		self.ses = ses
		self.email = email
		self.username = username
		self.password = password
		self.useragent = useragent
		self.userid = userid
		
	def reply(self, thread, message):
		return reply(self.ses, self.useragent, thread, message)
		
	def thread(self, forum, title, message):
		return thread(self.ses, self.useragent, forum, title, message)
