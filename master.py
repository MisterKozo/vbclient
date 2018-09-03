#!/usr/bin/env python

from forum import *
import sys
import signal
import random
import string
import time

VERSION = "0.1"
global user
user = None

def signal_handler(sig, frame):
	sys.stdout.write("\nType 'exit' (without apostrophes) to exit\n> ")
        sys.stdout.flush()
signal.signal(signal.SIGINT, signal_handler)

SEPARATOR = "|||"
def process_command(text):
	global user
	com = text.split(SEPARATOR)
	text_low = com[0].lower()
	if text_low == "exit":
		exit()
	elif text_low == "version":
		print("You are using version " + VERSION)
		return True
	elif text_low == "sleep":
		if len(com) < 2 or not com[1].isdigit():
			print("Syntax: sleep|||SECONDS")
			return False
		time.sleep(int(com[1]))
	elif text_low == "register":
		if len(com) < 2:
			print("Syntax: register|||USERNAME|||email(optional)")
			return False
		username = com[1]
		if len(com) >= 3:
			email = com[2]
		else:
			email = ''.join(random.choice(string.ascii_lowercase + string.digits) \
				for _ in range(random.randint(12,14)))+"@gmail.com"
		user = User(username=username, email=email)
		if user is None:
			print("Could not register. Please try different credentials")
		else:
			print("Logged into '{0}' with password '{1}'" \
				.format(user.username, user.password))
		return True
	elif text_low == "login":
		if len(com) < 2:
			print("Syntax: login|||USERNAME|||password")
			return False
		username = com[1]
		if len(com) >= 3:
			password = com[2]
			user = User(username=username, password=password)
		else:
			user = User(username=username)
		if user is None:
			print("Could not login. Please try different credentials")
		else:
			print("Logged into '{0}' with password '{1}'" \
				.format(user.username, user.password))
			#print("Session: {0}".format(user.ses.cookies))
		return True
	elif text_low == "post" and user is not None:
		if len(com) != 3:
			print("Syntax: post|||thread|||content")
			return False
		thread = com[1]
		#cut = len(text_low)+1+len(thread)+1
		message = com[2]
		res = user.reply(thread, message)
		if res:
			print("Posted successfully!")
		else:
			print("Error occurred, could not post!")
		return True
	elif text_low == "thread" and user is not None:
		if len(com) != 4:
			print("Syntax: thread|||num|||subject|||content")
			return False
		forum = com[1]
		title = com[2]
		message = com[3]
		res = user.thread(forum, title, message)
		if res:
			print("Posted successfully!")
		else:
			print("Error occurred, could not post!")
		return True
	elif text_low == "like" and user is not None:
		if len(com) != 2:
			print("Syntax: like|||postid")
			return False
		res = user.like(com[1])
	elif text_low == "batch":
		if len(com) != 2:
			print("Syntax: batch|||FILENAME")
			return False
		with open(com[1], 'r') as file_batch:
			for line in file_batch:
				if line[0] != "#":
					line = line[:-1]
					print(">> " + line)
					process_command(line)
		return True
	else:
		print("Unknown command: '{0}'".format(text_low))
		if user is None:
			print("(and/or you're logged out)")
		return False

while True:
	text = raw_input("> ")
	try:
		process_command(text)
	except Exception as e:
		print("Please log-in before executing forum-related commands!")
		print(str(e))
