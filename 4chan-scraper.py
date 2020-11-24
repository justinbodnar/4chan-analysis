# 4chan scraper
# by Justin Bodnar
# monitors the word frequency of a board

###########
# imports #
###########
from collections import OrderedDict
from textblob import TextBlob as tb
import traceback
import requests
import signal
import string
import math
import html
import json
import sys
import re

##########
# config #
##########
verbose = 0
errors = True


###########################
# TF-IDF helper functions #
###########################
# https://stevenloria.com/tf-idf/

# term frequency function
def tf(word, blob):
	return blob.words.count(word) / len(blob.words)

# returns num of documents containing a word
def n_containing(word, bloblist):
	return sum(1 for blob in bloblist if word in blob.words)

# inverse document frequency function
def idf(word, bloblist):
	return math.log(len(bloblist) / (1 + n_containing(word, bloblist)))

# computes the tf-idf score
def tfidf_score(word, blob, bloblist):
	return tf(word, blob) * idf(word, bloblist)

##################
# tfidf function #
##################
def tfidf( inputlist ):
	# allows input to be a list of strings
	bloblist = []
	for entry in inputlist:
		bloblist.append( tb(entry) )
	for i, blob in enumerate(bloblist):
		print("Top words in document {}".format(i + 1))
		scores = {word: tfidf_score(word, blob, bloblist) for word in blob.words}
		sorted_words = sorted(scores.items(), key=lambda x: x[1], reverse=True)
		for word, score in sorted_words[:3]:
			print("\tWord: {}, TF-IDF: {}".format(word, round(score, 5)))

#####################
# wordFreq function #
#####################
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

#######################
# getThreads function #
#######################
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

######################
# getThread function #
######################
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
		except Exception as e:
			# print stacktrace
			if errors:
				traceback.print_exc()
	# return array
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
i = 0
for thread in threads:
	i += 1
	if i > 10:
		break
	comments = getThread( board, thread )
	temp_string = ""
	for comment in comments:
		temp_string += comment + " "
	all_comments.append( temp_string )

# get word frequency
#wordFreq( all_comments )

# get tfidf
tfidf( all_comments )
