from fake_useragent import UserAgent
import requests
import hashlib
import os
import random
import string
import pickle
import time

URL_BASE     = "https://www.fxp.co.il/"
#URL_BASE = "http://127.0.0.1:5000/"
URL_REGISTER = URL_BASE + "register.php?do=addmember"
URL_LOGIN    = URL_BASE + "login.php?do=login"
URL_REPLY    = URL_BASE + "newreply.php?do=postreply&t="
URL_THREAD   = URL_BASE + "newthread.php?do=postthread&f="
URL_LIKE     = URL_BASE + "ajax.php?do=add_like"

def string_to_hex(string):
	return '%'.join("{:02x}".format(ord(c)) for c in string)
	
def text_between(s, first, second):
	try:
		return s.split(first)[1].split(second)[0]
	except:
		return None
		
def get_token(ses):
	res = ses.post(target, headers=header)
	return res.text.split('<input type="hidden" name="securitytoken" value="')[1].split('"')[0]

def register(ses, email, username, password, useragent):
	username = username.replace("\n", "")
	password = password.replace("\n", "")
	email = email.replace("\n", "")
	useragent = useragent.replace("\n", "")
	print("Registering\nUser: {0}\nPass: {1}\nEmail: {2}".format(username, password, email))
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
	#print(res.text)
	return res if "<strong>{0}</strong>".format(username) in res.text else None

def login(ses, username, password, useragent):
	username = username.replace("\n", "")
	password = password.replace("\n", "")
	useragent = useragent.replace("\n", "")
	password_md5 = hashlib.md5(password).hexdigest()
	print("Logging into {0}".format(username))
	header = {
		'User-Agent': useragent
	}
	data = {
		#dynamic
		'vb_login_username': username,
		'vb_login_password': password,
		'vb_login_md5password': password_md5,
		'vb_login_md5password_utf': password_md5,
		'postvars': '0',
		'cookieuser': '1',
		'logintype': '',
		'cssprefs': '',
		#hidden
		's': "",
		'securitytoken': "guest",
		'do': "login",
		'url': URL_BASE,
	}
	res = ses.post(URL_LOGIN, headers=header, data=data)
	userid = text_between(res.text, 'var USER_ID_FXP = "', '"')
	if userid.isdigit() and int(userid) > 0:
		url_session = URL_BASE + "?" +text_between(res.text, 'var SESSIONURL = "', '"')
		#print(ses.post(URL_BASE, headers=header).text)
		return res
	else:
		return None
	
def reply(ses, useragent, thread, message):
	target = URL_REPLY + thread
	header = {
		'User-Agent': useragent
	}
	
	res = ses.post(target, headers=header)
	#print(res.text)
	token = res.text.split('<input type="hidden" name="securitytoken" value="')[1].split('"')[0]
	userid = res.text.split('var USER_ID_FXP = "')[1].split('"')[0]
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
	#print(res.text)
	return '<div class="blockrow error" id="qr_error_td"></div>' in res.text
	
def thread(ses, useragent, forum, title, message):
	target = URL_THREAD + forum
	print("Posting to "+str(forum))
	header = {
		'User-Agent': useragent
	}
	res = ses.post(target, headers=header)
	token = res.text.split('<input type="hidden" name="securitytoken" value="')[1].split('"')[0]
	#userid = res.text.split('<input type="hidden" name="loggedinuser" value="')[1].split('"')[0]
	userid = res.text.split('var USER_ID_FXP = "')[1].split('"')[0]
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
	
def like(ses, useragent, postid):
	header = {
		'User-Agent': useragent,
		'Origin': URL_BASE[:-1]
	}
	res = ses.post("{0}showthread.php?p={1}".format(URL_BASE, postid), headers=header)
	print(res.text)
	#cls1 = res.text.split(' onclick="makelike(this.id);"')[0]
	#cls2 = cls1.split('"')
	#cls = cls2[-1]
	#cls = text_between(res.text, '"', ' onclick="makelike(this.id);"')
	token = res.text.split('<input type="hidden" name="securitytoken" value="')[1].split('"')[0]
	#userid = res.text.split('<input type="hidden" name="loggedinuser" value="')[1].split('"')[0]
	userid = res.text.split('var USER_ID_FXP = "')[1].split('"')[0]
	data = {
		'do': 'add_like',
		'postid': str(postid),
		'fxppro': '',
		'securitytoken': str(token)
	}
	print(data)
	res = ses.post(URL_LIKE, headers=header, data=data)
	print("Tried to like "+str(postid))
	#print(res.text)
	return res
	
class User(object):
	def __new__(cls, username, password=None, email=None):
		#hi, i want to access username
		file_path = "users/"+username
		#check if exists in db, if so, load instance
		if os.path.isfile(file_path):
			return pickle.load(open(file_path, 'r'))
		#doesnt exist in db! make sure theres an email
		if email is None and password is None:
			return None
		ses = requests.Session()
		useragent = UserAgent().random
		username = username
		if password is None:
			password = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) \
				for _ in range(random.randint(6,12)))
			res = register(ses, email, username, password, useragent)
		elif email is None:
			res = login(ses, username, password, useragent)
		#if cannot register return none
		if res is None:
			return None
		#didnt return, we have the cookies!
		#print(res.text)
		userid = res.text.split('var USER_ID_FXP = "')[1].split('"')[0]
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
		
	def like(self, postid):
			return like(self.ses, self.useragent, postid)
