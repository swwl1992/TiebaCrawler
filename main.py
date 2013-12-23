#!/usr/bin
# Tieba Crawler
# Author: Simon Wan Wenli
# Created on 17 Dec 2013

import os
import sys
import urllib2
import config
from HTMLParser import HTMLParser

ofile_dir = config.EXPORT_DIR + config.URL[-10:] + config.OUTPUT_FORMAT

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
	last_num = extract(pages_html[-1], 'pn=', '"')[0]
	return int(last_num[3:-1])

class TitleParser(HTMLParser):
	def handle_data(self, data):
		write_file('Title' + config.DELIMITER + data + '\n')
		if config.VERBOSE:
			print 'Title:', data

class UsernameParser(HTMLParser):
	def handle_data(self, data):
		append_file(data + config.DELIMITER)
		if config.VERBOSE:
			print 'Username:', data

class PostParser():
	def feed(self, data):
		raw_content = extract(data, '>', '</div>')[0]
		# remove next line and whitespace
		post_content = raw_content[1:-6].\
			replace('\n', '').replace(' ', '')
		append_file(post_content + config.DELIMITER)
		if config.VERBOSE:
			print 'Post:', post_content

class PageCrawler():
	def __init__(self):
		pass

	def run(self, url):
		# get response html
		self.response = urllib2.urlopen(url)
		self.html = self.response.read()
		self.html = self.html.decode(charset)

		# get usernames	
		append_file('\nUsernames' + config.DELIMITER)
		lis_html = extract(self.html, config.LI_START, config.LI_END)
		username_parser = UsernameParser()
		if lis_html:
			if config.VERBOSE:
				print 'No. of users:', len(lis_html)
			for li_html in lis_html:
				as_html = extract(li_html, config.A_START, config.A_END)
				for a_html in as_html:
					username_parser.feed(a_html)
		append_newline()

		# get posts	
		append_file('Posts' + config.DELIMITER)
		posts_html = extract(self.html, config.POST_START, config.POST_END)
		post_parser = PostParser()
		if posts_html:
			if config.VERBOSE:
				print 'No. of posts:', len(posts_html)
			for post_html in posts_html:
				post_parser.feed(post_html)
		append_newline()

# get response from source and decode it
response = urllib2.urlopen(config.URL)
html = response.read()
charset = response.headers.getparam('charset')
print "Source encoding:", charset
html = html.decode(charset)

title_html = extract(html, config.TITLE_START, config.TITLE_END)
title_parser = TitleParser()
title_parser.feed(title_html[0])

last_page_num = get_last_pagenum(html)

for page_num in range(1, last_page_num + 1):
	url = config.URL + '?pn=' + str(page_num)
	append_file('Page' + config.DELIMITER + str(page_num))
	pc = PageCrawler()
	pc.run(url)
