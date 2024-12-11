"""
4chan Scraper
Monitors word frequency on a specified board.
By Justin Bodnar (justinbodnar.com)
"""

# Imports
from prettytable import PrettyTable
from collections import Counter
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import re
import html
import traceback
import sys

# Config
verbosity = 1  # 0: minimal output, 1: detailed output
errors = True
max_threads = 50  # Number of threads to process (set to None for all threads)

def load_stop_words(file_path="words_to_ignore.txt"):
	"""
	Load stop words from a specified file.
	
	Args:
		file_path (str): Path to the file containing stop words.
	
	Returns:
		set: A set of stop words in lowercase.
	"""
	with open(file_path, "r") as f:
		return set(word.strip().lower() for word in f.readlines())

stop_words = load_stop_words()

def word_freq(text_array, board):
	"""
	Calculate and display word frequencies from a list of text data.
	
	Args:
		text_array (list): List of strings containing text to analyze.
		board (str): The name of the 4chan board being analyzed.
	"""
	text = " ".join(text_array)
	words = re.findall(r'\b[a-z]{3,15}\b', text.lower())
	filtered_words = [word for word in words if word not in stop_words]
	frequency = Counter(filtered_words)
	sorted_frequency = sorted(frequency.items(), key=lambda x: x[1], reverse=True)

	# Create a pretty table
	table = PrettyTable()
	table.field_names = ["Word", "Frequency"]

	# Add rows for the top 50 words
	for word, count in sorted_frequency[:50]:
		table.add_row([word, count])

	# Print the table
	print("\nTop 50 Words:")
	print(table)

def get_threads(board):
	"""
	Fetch thread IDs from a specified 4chan board.
	
	Args:
		board (str): The name of the 4chan board to scrape.
	
	Returns:
		list: A list of thread IDs.
	"""
	url = f"https://a.4cdn.org/{board}/threads.json"
	if verbosity > 0:
		print("\nFetching threads:", url)
	response = requests.get(url)
	threads = []
	titles = []
	for page in response.json():
		for thread in page["threads"]:
			threads.append(thread["no"])
			if verbosity > 0 and "sub" in thread:
				titles.append(thread["sub"])
	if verbosity > 0:
		print("\nThread Titles:")
		for title in titles:
			print(f"- {title}")
	return threads

def get_thread(board, thread_id):
	"""
	Fetch and clean text content from a specific 4chan thread.
	
	Args:
		board (str): The name of the 4chan board.
		thread_id (int): The thread ID to fetch content from.
	
	Returns:
		list: A list of cleaned text content from the thread.
	"""
	url = f"https://a.4cdn.org/{board}/thread/{thread_id}.json"
	if verbosity > 0:
		print(f"Fetching thread: {url}")
	try:
		response = requests.get(url)
		data = response.json()
		replies = []
		for post in data["posts"]:
			try:
				com = post.get("com", "")
				com = html.unescape(com)
				com = re.sub('<.*?>', '', com)
				com = re.sub(r'>>\d+', '', com)
				com = re.sub(r'http[s]?://\S+', '', com)
				com = re.sub(r'[^a-zA-Z\s]', '', com)
				com = re.sub(r'\s+', ' ', com).strip()
				replies.append(com.lower())
			except Exception as e:
				if errors:
					traceback.print_exc()
		return replies
	except Exception as e:
		if errors:
			traceback.print_exc()
		return []

# Main routine
if len(sys.argv) < 2:
	print("You must enter a board to scrape")
	print("Example: python3 4chan-scraper.py b")
	sys.exit()

board = sys.argv[1]
threads = get_threads(board)
threads_to_process = threads[:max_threads] if max_threads else threads

all_comments = []

for i, thread in enumerate(threads_to_process):
	comments = get_thread(board, thread)
	all_comments.append(" ".join(comments))

# Output word frequency
word_freq(all_comments, board)

# Print verbose information at the end
if verbosity > 0:
	print(f"\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
	print(f"Analyzed Board: {board}")
	print(f"Verbosity: {verbosity}")
	print(f"Total Threads Analyzed: {len(threads_to_process)}")
	if len(all_comments) > 0:
		print(f"Total Comments Retrieved: {sum(len(c.split()) for c in all_comments):,} words\n")
