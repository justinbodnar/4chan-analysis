# 4chan Word Frequency Scraper

A Python-based tool to monitor word frequency on a specified 4chan board. Written by [Justin Bodnar](https://justinbodnar.com), this script processes posts, filters common words, and outputs the most frequently used words in descending order.

---

## Features
- Fetches posts from 4chan boards using the `requests` library.
- Counts and ranks word usage by frequency, excluding common words from a customizable list `words_to_ignore.txt`.
- Outputs the top 50 words in a clean table format.
- Configurable verbosity and thread limits via hardcoded variables:
  - `verbose`: Controls output detail (0 for minimal, 2 for detailed).
  - `max_threads`: Limits the number of threads processed (set to `None` to process all threads).

---

## Quick Start

### Clone the Repository
```bash
git clone https://github.com/justinbodnar/4chan-analysis.git
cd 4chan-analysis
```

### Install Requirements
```bash
pip3 install -r requirements.txt
```

### Run the Script
```bash
python3 4chan-scraper.py [board]
```
Replace `[board]` with the desired 4chan board (e.g., `b`, `biz`, `pol`).

---

## File Descriptions

### `4chan-scraper.py`
- **Main script**: Scrapes a specified board and generates word frequency analysis.
- **Verbose Mode**: Provides thread titles and detailed statistics when `verbose` is set to `1`.
- **Custom Stop Words**: Utilizes `words_to_ignore.txt` to filter out common and unwanted words.
- **Configuration Variables**:
  - `verbose`: Adjust verbosity level (0 or 1).
  - `max_threads`: Set the number of threads to analyze (default is 50).

### `words_to_ignore.txt`
- Contains words to exclude from the analysis.

---

## Example Verbose Output
```plaintext
Fetching threads: https://a.4cdn.org/biz/threads.json

Thread Titles:
Fetching thread: https://a.4cdn.org/biz/thread/45310862.json
Fetching thread: https://a.4cdn.org/biz/thread/59406325.json
Fetching thread: https://a.4cdn.org/biz/thread/59406391.json

...

|   token   |     38    |
|    yeah   |     38    |
|    post   |     37    |
|    nice   |     37    |
|    feel   |     37    |
|    bad    |     36    |
|    pump   |     36    |
| chainlink |     36    |
|    pay    |     35    |
+-----------+-----------+

Date: 2024-12-11 00:13:01
Analyzed Board: biz
Verbosity: 1
Total Threads Analyzed: 100
Total Comments Retrieved: 67,633 words
```
