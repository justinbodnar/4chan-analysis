# 4chan scraper
# by Justin Bodnar
# monitors the word frequency of a board

# imports
from collections import OrderedDict
import traceback
import requests
import signal
import string
import html
import json
import sys
import re

# config
verbose = 0
errors = True

# wordFreq function
# takes an array of strings
# prints a frequency list
# taken from https://code.tutsplus.com/tutorials/counting-word-frequency-in-a-file-using-python--cms-25965
def wordFreq ( text_array ):
	# create one string from all input
	text = ""
	for subtext in text_array:
		text += subtext + " "
	# create frequency dictionary
	frequency = {}
	match_pattern = re.findall(r'\b[a-z]{3,15}\b', text)
	for word in match_pattern:
		count = frequency.get(word,0)
		frequency[word] = count + 1
	frequency_list = frequency.keys()
	# sort by dict values
#	for words in OrderedDict(sorted(frequency.items(), key=lambda kv: kv[1]['key3'], reverse=True)):
	for words in dict(sorted(frequency.items(), key=lambda item: item[1])):
		if( frequency[words] > 1 ):
			print( words, frequency[words] )

# getThreads function
# takes a string of the board ( example: "pol" )
# returns a list of thread IDs ( example [ 12345, 12346, 12347 ] )
def getThreads( board ):
	global verbose
	# create URL
	url = "https://a.4cdn.org/"+board+"/threads.json"
	# output
	if verbose > 0:
		print( "getThreads function called" )
		print( "URL: " + url )
	# get content of URL
	r = requests.get( url )
	# convert string into JSON
	j = json.loads( r.text )

	# create list for return
	threads = []

	# for each page
	for page in j:
		# for each thread on page
		for thread in page["threads"]:
			# add to threads list
			threads.append( thread["no"] )
	# output
	if verbose > 0:
		print( str(len(threads)) + " threads found" )

	# return thread ids
	return threads

# getThread function
# takes a board name,
# and a thread id
# returns the plaintext of the thread
def getThread( board, thread ):
	global verbose
	# avoid type errors
	thread = str(thread)
	# create URL
	url = "https://a.4cdn.org/"+board+"/thread/"+thread+".json"
	# output
	if verbose:
		print( "getThread function called" )
		print( "URL: " + url )
	# get response from URL
	r = requests.get( url )
	# convert to JSON
	j = json.loads( r.text )

	# creat list for return
	replies = []

	# for each comment in the thread
	for each in j["posts"]:
		# try-catch for textless comments
		try:
			# remove HTML
			com = each["com"]
			if len(com) > 500:
				next
			# replace linebreaks with spaces
			com = re.sub('<br />|<br/>|<br>',' ',com)
			# remove HTML
			cleanr = re.compile('<.*?>')
			com = re.sub(cleanr, '', com)
			# html decode entities
			com = html.unescape( com )
			# remove comment replies
			i = 0
			while ">>" in com and i < 10:
				i += 1
				start = com.find('>>')
				end = com[start:].find(' ')
				com = com[:start] + com[end+1:]
			# remove urls
			pattern = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
			com = pattern.sub('', com )
			# remove non-alpha chars
			com = re.sub(r'[^A-Za-z ]+', '', com)
			# remove dupe spaces
			j = 0
			while "  " in com and j < 10:
				j += 1
				com = re.sub("  ", " ", com)
			# make stirng lowercase
			com = com.lower()
			if i < 10 and j < 10:
				replies.append( com )
			aszd.zdf
		except Exception as e:
			# print stacktrace
			if errors:
				traceback.print_exc()
	return replies

################
# main routine #
################

# get arguments
if len(sys.argv) < 2:
	print( "You must enter a board to scrape" )
	print( "Example: python scrape.py b" )
	exit()
else:
	board = sys.argv[1]

# get all threads
threads = getThreads( board )

# get all comments from all threads
all_comments = []
for thread in threads:
	comments = getThread( board, thread )
	for comment in comments:
		all_comments.append( comment )

# get word frequency
wordFreq( all_comments )
