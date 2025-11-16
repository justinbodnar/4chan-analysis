"""
4chan Scraper
Monitors word frequency on a specified board.
By Justin Bodnar (justinbodnar.com)
"""

# Imports
from prettytable import PrettyTable
from collections import Counter
from datetime import datetime
import requests
import re
import html
import traceback
import sys
from pathlib import Path

# Config
verbosity = 1  # 0: minimal output, 1: detailed output
errors = True
max_threads = 50  # Number of threads to process (set to None for all threads)

WORD_PATTERN = re.compile(r"\b[a-z]{3,15}\b")


def load_stop_words(file_path: str = "words_to_ignore.txt") -> set:
    """Return a set of lowercase stop words, falling back to a default list."""
    default_words = {
        "the",
        "and",
        "for",
        "that",
        "with",
        "have",
        "this",
        "you",
        "but",
    }
    try:
        stop_path = Path(file_path)
        with stop_path.open("r", encoding="utf-8") as f:
            return set(word.strip().lower() for word in f.readlines() if word.strip())
    except FileNotFoundError:
        if errors:
            print(
                f"Stop words file '{file_path}' was not found. Falling back to a default list."
            )
    return default_words


stop_words = load_stop_words()


def tokenize_text(text_array):
    """Tokenize raw text, lowercase it, and remove common stop words."""
    text = " ".join(text_array)
    words = WORD_PATTERN.findall(text.lower())
    return [word for word in words if word not in stop_words]


def word_freq(filtered_words):
    """Return a word frequency counter for the supplied tokens."""
    return Counter(filtered_words)


def display_word_table(frequency: Counter, limit: int = 50):
    """Print a table containing the most frequent words."""
    sorted_frequency = sorted(frequency.items(), key=lambda x: x[1], reverse=True)
    table = PrettyTable()
    table.field_names = ["Word", "Frequency"]
    for word, count in sorted_frequency[:limit]:
        table.add_row([word, count])
    print("\nTop 50 Words:")
    print(table)


def compute_text_metrics(filtered_words, frequency):
    """Compute aggregate statistics for the analyzed tokens."""
    word_count = len(filtered_words)
    unique_words = len(frequency)
    hapax_legomena = sum(1 for count in frequency.values() if count == 1)
    avg_word_length = (
        (sum(len(word) for word in filtered_words) / word_count) if word_count else 0
    )
    lexical_diversity = (unique_words / word_count) if word_count else 0
    return {
        "Total Filtered Words": f"{word_count:,}",
        "Unique Words": f"{unique_words:,}",
        "Lexical Diversity": f"{lexical_diversity:.3f}",
        "Avg. Word Length": f"{avg_word_length:.2f}",
        "Hapax Legomena": f"{hapax_legomena:,}",
    }


def display_metrics(metrics):
    """Pretty print the computed text metrics."""
    table = PrettyTable()
    table.field_names = ["Metric", "Value"]
    for metric, value in metrics.items():
        table.add_row([metric, value])
    print("\nText Metrics:")
    print(table)


def get_ngrams(filtered_words, n=2):
    """Return a Counter of n-grams for the provided token list."""
    if len(filtered_words) < n:
        return Counter()
    ngrams = zip(*[filtered_words[i:] for i in range(n)])
    return Counter([" ".join(gram) for gram in ngrams])


def display_ngram_table(counter: Counter, label: str, limit: int = 15):
    """Display the most frequent n-grams for the specified counter."""
    if not counter:
        print(f"\nNo {label.lower()} were detected.")
        return
    sorted_items = counter.most_common(limit)
    table = PrettyTable()
    table.field_names = [label, "Frequency"]
    for phrase, count in sorted_items:
        table.add_row([phrase, count])
    print(f"\nTop {limit} {label}:")
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
    all_comments.extend(comments)

# Output analyses
filtered_words = tokenize_text(all_comments)
frequency = word_freq(filtered_words)
display_word_table(frequency)
display_metrics(compute_text_metrics(filtered_words, frequency))
display_ngram_table(get_ngrams(filtered_words, 2), "Bigrams")
display_ngram_table(get_ngrams(filtered_words, 3), "Trigrams")

# Print verbose information at the end
if verbosity > 0:
    print(f"\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Analyzed Board: {board}")
    print(f"Verbosity: {verbosity}")
    print(f"Total Threads Analyzed: {len(threads_to_process)}")
    if len(all_comments) > 0:
        total_words = sum(len(c.split()) for c in all_comments)
        print(f"Total Comments Retrieved: {len(all_comments):,}")
        print(f"Total Raw Words: {total_words:,}")
        print(f"Total Filtered Words: {len(filtered_words):,}\n")
