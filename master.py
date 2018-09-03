from forum import *
import sys
import signal

VERSION = "0.1"

def signal_handler(sig, frame):
	sys.stdout.write("\nType 'exit' (without apostrophes) to exit\n> ")
        sys.stdout.flush()
signal.signal(signal.SIGINT, signal_handler)

if len(sys.argv) == 3:
	user = User(sys.argv[1], sys.argv[2])
elif len(sys.argv) == 2:
	user = User(sys.argv[1])
else:
	print("Syntax: {0} USERNAME email(if registering)".format(sys.argv[0]))
	exit()

if user is None:
	print("Could not login/register. Please try different credentials")
	exit()
print("Logged into '{0}' with password '{1}'" \
	.format(user.username, user.password))

SEPARATOR = "|||"
def process_command(text):
	com = text.split(SEPARATOR)
	text_low = com[0].lower()
	if text_low == "exit":
		exit()
	elif text_low == "version":
		print("You are using version " + VERSION)
		return True
	elif text_low == "post":
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
	elif text_low == "batch":
		if len(com) != 2:
			print("Syntax: batch|||FILENAME")
			return False
		with open(com[1], 'r') as file_batch:
			for line in file_batch:
				process_command(line)
		return True
	elif text_low == "thread":
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
	else:
		print("Unknown command: '{0}'".format(text_low))
		return False

while True:
	text = raw_input("> ")
	process_command(text)
