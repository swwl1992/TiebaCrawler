#!/usr/bin
# Tieba Crawler
# Author: Simon Wan Wenli
# Created on 17 Dec 2013

import os
import sys
import urllib2
import config
import argparse
from HTMLParser import HTMLParser


def clear_lists():
	posts[:] = []
	contents[:] = []
	pids[:] = []
	
def write_file(msg):
	ofile = open(ofile_dir, 'w')
	ofile.write(msg.encode(config.OUTPUT_ENCODING))
	ofile.close()

def append_file(msg):
	ofile = open(ofile_dir, 'a')
	ofile.write(msg.encode(config.OUTPUT_ENCODING))
	ofile.close()

def append_newline():
	append_file('\n')

def extract(text, start_pattern, end_pattern):
	output = []
	start = text.find(start_pattern)
	end  = text.find(end_pattern, start)
	while start != -1 and end != -1:
		output.append(text[start: end + len(end_pattern)])
		start = text.find(start_pattern, end)
		end  = text.find(end_pattern, start)
	return output

def get_last_pagenum(html):
	pager_html = extract(html, config.PAGER_START, config.PAGER_END)
	pages_html = extract(pager_html[0], config.A_START, config.A_END)
	if pages_html:
		last_num = extract(pages_html[-1], 'pn=', '"')[0]
		return int(last_num[3:-1])
	else:
		return 1

class TitleParser(HTMLParser):
	def handle_data(self, data):
		write_file('Title' + config.DELIMITER + data)
		print 'Title:', data

class UsernameParser(HTMLParser):
	def handle_data(self, data):
		post = Post()
		post.set_author(data)
		posts.append(post)
		# append_file(data + config.DELIMITER)
		if VERBOSE:
			print 'Username:', data

class PostParser():
	def __init__(self):
		pass

	def feed(self, data):
		raw_content = extract(data, '>', '</div>')[0]
		pid = data[22:33]
		pids.append(pid)
		# remove next line
		content = raw_content[1:-6].replace('\n', '')
		contents.append(content)
		# append_file(post_content + config.DELIMITER)
		if VERBOSE:
			print 'Post Content:', post_content

class Post():
	def __init__(self):
		self.pid = 0
		self.author = ""
		self.cont = ""
		self.replies = []

	def set_pid(self, i):
		self.pid = i

	def set_author(self, a):
		self.author = a
	
	def set_cont(self, c):
		self.cont = c

	def set_replies(self, r):
		self.replies = r

	def to_string(self):
		print 'PID:', self.pid
		print 'Author:', self.author
		print 'Content:', self.cont
		print 'Replies:', self.replies

class PageCrawler():
	def __init__(self):
		pass

	def run(self, url):
		# get response html
		self.response = urllib2.urlopen(url)
		self.html = self.response.read()
		self.html = self.html.decode(charset)

		# get usernames	
		lis_html = extract(self.html, config.UID_START, config.UID_END)
		username_parser = UsernameParser()
		if lis_html:
			for li_html in lis_html:
				as_html = extract(li_html,\
					config.A_START, config.A_END)
				for a_html in as_html:
					username_parser.feed(a_html)

		# get posts	
		posts_html = extract(self.html,\
			config.POST_START, config.POST_END)
		post_parser = PostParser()
		if posts_html:
			for post_html in posts_html:
				post_parser.feed(post_html)

		# set post content
		for (post, content) in zip(posts, contents):
			post.set_cont(content)

		# set post pids
		for (post, pid) in zip(posts, pids):
			post.set_pid(pid)

		# set replies to the post based on the pid
		replies_html = extract(self.html,\
			config.REPLIES_START, config.REPLIES_END)
		for reply_html in replies_html:
			raw_pid = extract(reply_html,\
				config.PID_START, config.PID_END)[0]
			pid = raw_pid[-12:-1]
			if VERBOSE:
				print 'PID:', pid
			wrapped_author = extract(reply_html,\
				config.REPLY_AUTH_START, config.REPLY_AUTH_END)[0]
			raw_author = extract(wrapped_author, '<a', '</a>')[0]
			author = extract(raw_author, '>', '<')[0]
			reply = author[1:-1]
			raw_content = extract(reply_html,\
				config.REPLY_CONT_START, config.REPLY_CONT_END)[0]
			content = extract(raw_content,\
				'>', config.REPLY_CONT_END)[0]
			reply += ":"
			reply += content[1:-8].replace(' ', '')
			if VERBOSE:
				print reply
			for post in posts:
				if str(post.pid) == pid:
					post.replies.append(reply)

		# write usernames to file
		append_file('\nUsername')
		for post in posts:
			append_file(config.DELIMITER + post.author)

		# write post content to file
		append_file('\nPost content')
		for post in posts:
			append_file(config.DELIMITER + post.cont)

		# write replies to file
		append_file('\nReplies')
		for post in posts:
			append_file(config.DELIMITER)
			for reply in post.replies:
				append_file(reply + ';')

##
# Main section
##

# process command line args
parser = argparse.ArgumentParser(description='Crawl from Tieba Baidu')
parser.add_argument('-v', dest='verbose', action='store_true',
	help='verbose additional info')
parser.add_argument('url', type=str,
	help='crawl from a URL with "http://" in front')
args = parser.parse_args()
VERBOSE = args.verbose
URL = args.url

if not os.path.exists(config.EXPORT_DIR):
	os.mkdir(config.EXPORT_DIR)
	print 'Make directory:', config.EXPORT_DIR
ofile_dir = config.EXPORT_DIR + URL[-10:] + config.OUTPUT_FORMAT
posts =		[]
contents =	[]
pids = 		[]

# get response from source and decode it
response = urllib2.urlopen(URL)
html = response.read()
charset = response.headers.getparam('charset')
print 'Response from:', URL
print 'Source encoding:', charset
print 'Output encoding:', config.OUTPUT_ENCODING 
html = html.decode(charset)

title_html = extract(html, config.TITLE_START, config.TITLE_END)
title_parser = TitleParser()
title_parser.feed(title_html[0])

last_page_num = get_last_pagenum(html)

floor_no = 1
for page_num in range(1, last_page_num + 1):
	url = URL + '?pn=' + str(page_num)
	append_file('\nPage' + config.DELIMITER + str(page_num))
	pc = PageCrawler()
	pc.run(url)

	# write floor no. to file
	append_file('\nFloor No.')
	for post in posts:
		append_file(config.DELIMITER + str(floor_no))
		floor_no += 1

	# clear all the lists
	print '\tPage ' + str(page_num) + ' complete.'
	print '\tPosts No.: ', len(posts)
	clear_lists()

print 'Exported to ' + ofile_dir
print 'Crawling complete.'
