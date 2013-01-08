# -*- coding: utf-8 -*-
import re
import httplib
import socket
import urlparse
import urllib
import threading
import time
import wikitools
from Queue import Queue

USERNAME = ''
PASSWORD = ''
WIKI_API = r'http://wiki.tf2.com/w/api.php'
OUTPUT_PAGE = r''
IGNORE_LIST = r''
NUM_THREADS = 50

wiki = wikitools.Wiki(WIKI_API)
wiki.login(username=USERNAME, password=PASSWORD)


def is_good_title(title):
	langs = ['ar', 'cs', 'da', 'de', 'es', 'fi' ,'fr', 'hu', 'it', 'ja', 'ko', 'nl', 'no', 'pl', 'pt', 'pt-br', 'ro', 'ru', 'sv', 'tr', 'zh-hans', 'zh-hant']
	for lang in langs:
		if title.endswith('/' + lang):
			return False
	return True

def get_all_articles():
	params = {
		'action': 'query',
		'list': 'allpages',
		'aplimit': '5000',
		'apfilterredir': 'nonredirects'
		}

	print 'Getting list of articles from API...'

	req = wikitools.api.APIRequest(wiki, params)
	res = req.query(querycontinue=True)

	print 'Done'

	output = [ page['title'] for page in res['query']['allpages'] if is_good_title(page['title']) ]

	return output

def strip_slashes(url):
	if url.endswith('/') or url.endswith('\\'):
		return url[:-1]
	return url

class Log(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.lines = []
		self.start()

	def add(self, line):
		self.lines.append(line)

	def run(self):
		while True:
			if len(self.lines) > 0:
				print(self.lines.pop(0))

class Worker(threading.Thread):
	"""Thread executing tasks from a given tasks queue"""
	def __init__(self, tasks):
		threading.Thread.__init__(self)
		self.tasks = tasks
		self.daemon = True
		self.start()
	
	def run(self):
		while True:
			func, args, kargs = self.tasks.get()
			try: func(*args, **kargs)
			except Exception, e: print e
			self.tasks.task_done()


class ThreadPool:
	"""Pool of threads consuming tasks from a queue"""
	def __init__(self, num_threads):
		self.tasks = Queue(num_threads)
		for _ in range(num_threads): Worker(self.tasks)

	def add_task(self, func, *args, **kargs):
		"""Add a task to the queue"""
		self.tasks.put((func, args, kargs))

	def wait_completion(self):
		"""Wait for completion of all the tasks in the queue"""
		self.tasks.join()


class LinkChecker(object):
	'''
	Given a HTTP URL, tries to load the page from the Internet and checks if it
	is still online.

	Returns a (boolean, string) tuple saying if the page is online and including
	a status reason.

	Warning: Also returns false if your Internet connection isn't working
	correctly! (This will give a Socket Error)
	'''
	def __init__(self, url, redirectChain = [], serverEncoding=None, HTTPignore=[]):
		"""
		redirectChain is a list of redirects which were resolved by
		resolve_redirect(). This is needed to detect redirect loops.
		"""
		self.url = url
		self.serverEncoding = serverEncoding
		self.header = {
			'User-agent': 'Mozilla/5.0 (X11; U; Linux i686; de; rv:1.8) Gecko/20051128 SUSE/1.5-0.1 Firefox/1.5',
			'Accept': 'text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5',
			'Accept-Language': 'de-de,de;q=0.8,en-us;q=0.5,en;q=0.3',
			'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
			'Keep-Alive': '30',
			'Connection': 'keep-alive',
		}
		self.redirectChain = redirectChain + [url]
		self.change_url(url)
		self.HTTPignore = HTTPignore

	def get_connection(self):
		if self.scheme == 'http':
			return httplib.HTTPConnection(self.host, timeout=30)
		elif self.scheme == 'https':
			return httplib.HTTPSConnection(self.host, timeout=30)

	def get_encoding_used_by_server(self):
		if not self.serverEncoding:
			try:
				print(u'Contacting server %s to find out its default encoding...' % self.host)
				conn = self.get_connection()
				conn.request('HEAD', '/', None, self.header)
				self.response = conn.getresponse()

				self.read_encoding_from_response(response)
			except:
				pass
			if not self.serverEncoding:
				# TODO: We might also load a page, then check for an encoding
				# definition in a HTML meta tag.
				print(u'Error retrieving server\'s default charset. Using ISO 8859-1.')
				# most browsers use ISO 8859-1 (Latin-1) as the default.
				self.serverEncoding = 'iso8859-1'
		return self.serverEncoding

	def read_encoding_from_response(self, response):
		if not self.serverEncoding:
			try:
				ct = response.getheader('Content-Type')
				charsetR = re.compile('charset=(.+)')
				charset = charsetR.search(ct).group(1)
				self.serverEncoding = charset
			except:
				pass

	def change_url(self, url):
		self.url = url
		# we ignore the fragment
		self.scheme, self.host, self.path, self.query, self.fragment = urlparse.urlsplit(self.url)
		if not self.path:
			self.path = '/'
		if self.query:
			self.query = '?' + self.query
		self.protocol = url.split(':', 1)[0]
		# check if there are non-ASCII characters inside path or query, and if
		# so, encode them in an encoding that hopefully is the right one.
		try:
			self.path.encode('ascii')
			self.query.encode('ascii')
		except UnicodeEncodeError:
			encoding = self.get_encoding_used_by_server()
			self.path = unicode(urllib.quote(self.path.encode(encoding)))
			self.query = unicode(urllib.quote(self.query.encode(encoding), '=&'))

	def resolve_redirect(self, useHEAD = False):
		'''
		Requests the header from the server. If the page is an HTTP redirect,
		returns the redirect target URL as a string. Otherwise returns None.

		If useHEAD is true, uses the HTTP HEAD method, which saves bandwidth
		by not downloading the body. Otherwise, the HTTP GET method is used.
		'''
		conn = self.get_connection()
		try:
			if useHEAD:
				conn.request('HEAD', '%s%s' % (self.path, self.query), None,
							 self.header)
			else:
				conn.request('GET', '%s%s' % (self.path, self.query), None,
							 self.header)
			self.response = conn.getresponse()
			# read the server's encoding, in case we need it later
			self.read_encoding_from_response(self.response)
		except httplib.BadStatusLine:
			# Some servers don't seem to handle HEAD requests properly,
			# e.g. http://www.radiorus.ru/ which is running on a very old
			# Apache server. Using GET instead works on these (but it uses
			# more bandwidth).
			if useHEAD:
				return self.resolve_redirect(useHEAD = False)
			else:
				raise
		if self.response.status >= 300 and self.response.status <= 399:
			#print response.getheaders()
			redirTarget = self.response.getheader('Location')
			if redirTarget:
				try:
					redirTarget.encode('ascii')
				except UnicodeError:
					redirTarget = redirTarget.decode(
						self.get_encoding_used_by_server())
				if redirTarget.startswith('http://') or \
				   redirTarget.startswith('https://'):
					self.change_url(redirTarget)
					return True
				elif redirTarget.startswith('/'):
					self.change_url(u'%s://%s%s'
								   % (self.protocol, self.host, redirTarget))
					return True
				else: # redirect to relative position
					# cut off filename
					directory = self.path[:self.path.rindex('/') + 1]
					# handle redirect to parent directory
					while redirTarget.startswith('../'):
						redirTarget = redirTarget[3:]
						# some servers redirect to .. although we are already
						# in the root directory; ignore this.
						if directory != '/':
							# change /foo/bar/ to /foo/
							directory = directory[:-1]
							directory = directory[:directory.rindex('/') + 1]
					self.change_url('%s://%s%s%s'
								   % (self.protocol, self.host, directory,
									  redirTarget))
					return True
		else:
			return False # not a redirect

	def check(self, useHEAD = False):
		"""
		Returns True and the server status message if the page is alive.
		Otherwise returns false
		"""
		try:
			wasRedirected = self.resolve_redirect(useHEAD = useHEAD)
		except UnicodeError, error:
			return False, u'Encoding Error: %s (%s)' \
				   % (error.__class__.__name__, unicode(error))
		except httplib.error, error:
			return False, u'HTTP Error: %s' % error.__class__.__name__
		except socket.error, error:
			# http://docs.python.org/lib/module-socket.html :
			# socket.error :
			# The accompanying value is either a string telling what went
			# wrong or a pair (errno, string) representing an error
			# returned by a system call, similar to the value
			# accompanying os.error
			if isinstance(error, basestring):
				msg = error
			else:
				try:
					msg = error[1]
				except IndexError:
					print u'### DEBUG information for #2972249'
					raise IndexError, type(error)
			# TODO: decode msg. On Linux, it's encoded in UTF-8.
			# How is it encoded in Windows? Or can we somehow just
			# get the English message?
			return False, u'Socket Error: %s' % repr(msg)
		if wasRedirected:
			if self.url in self.redirectChain:
				if useHEAD:
					# Some servers don't seem to handle HEAD requests properly,
					# which leads to a cyclic list of redirects.
					# We simply start from the beginning, but this time,
					# we don't use HEAD, but GET requests.
					redirChecker = LinkChecker(self.redirectChain[0],
											   serverEncoding=self.serverEncoding,
											   HTTPignore=self.HTTPignore)
					return redirChecker.check(useHEAD = False)
				else:
					urlList = ['[%s]' % url for url in self.redirectChain + [self.url]]
					return False, u'HTTP Redirect Loop: %s' % ' -> '.join(urlList)
			elif len(self.redirectChain) >= 19:
				if useHEAD:
					# Some servers don't seem to handle HEAD requests properly,
					# which leads to a long (or infinite) list of redirects.
					# We simply start from the beginning, but this time,
					# we don't use HEAD, but GET requests.
					redirChecker = LinkChecker(self.redirectChain[0],
											   serverEncoding=self.serverEncoding,
											   HTTPignore = self.HTTPignore)
					return redirChecker.check(useHEAD = False)
				else:
					urlList = ['[%s]' % url for url in self.redirectChain + [self.url]]
					return False, u'Long Chain of Redirects: %s' % ' -> '.join(urlList)
			else:
				redirChecker = LinkChecker(self.url, self.redirectChain,
										   self.serverEncoding,
										   HTTPignore=self.HTTPignore)
				return redirChecker.check(useHEAD = useHEAD)
		else:
			try:
				conn = self.get_connection()
			except httplib.error, error:
				return False, u'HTTP Error: %s' % error.__class__.__name__
			try:
				conn.request('GET', '%s%s'
							 % (self.path, self.query), None, self.header)
			except socket.error, error:
				return False, u'Socket Error: %s' % repr(error[1])
			try:
				self.response = conn.getresponse()
			except Exception, error:
				return False, u'Error: %s' % error
			# read the server's encoding, in case we need it later
			self.read_encoding_from_response(self.response)
			# site down if the server status is between 400 and 499
			alive = self.response.status not in range(400, 500)
			if self.response.status in self.HTTPignore:
				alive = False
			return alive, '%s %s' % (self.response.status, self.response.reason)

class WeblinkCheckerRobot:
	'''
	Robot which will use several LinkCheckThreads at once to search for dead
	weblinks on pages provided by the given generator.
	'''
	def __init__(self, pool, pages):
		self.pool = pool
		self.pages = pages
		self.links = []
		self.data = {}
		self.suspicious = {}
		self.log = Log()
		self.lock = threading.Lock()
		self.ignorelist = self.get_ignorelist()

	def return_link_regex(self, withoutBracketed=False, onlyBracketed=False):
		"""Return a regex that matches external links."""
		# RFC 2396 says that URLs may only contain certain characters.
		# For this regex we also accept non-allowed characters, so that the bot
		# will later show these links as broken ('Non-ASCII Characters in URL').
		# Note: While allowing dots inside URLs, MediaWiki will regard
		# dots at the end of the URL as not part of that URL.
		# The same applies to comma, colon and some other characters.
		notAtEnd = '\]\s\.:;,<>"\|)'
		# So characters inside the URL can be anything except whitespace,
		# closing squared brackets, quotation marks, greater than and less
		# than, and the last character also can't be parenthesis or another
		# character disallowed by MediaWiki.
		notInside = '\]\s<>"'
		# The first half of this regular expression is required because '' is
		# not allowed inside links. For example, in this wiki text:
		#	   ''Please see http://www.example.org.''
		# .'' shouldn't be considered as part of the link.
		regex = r'(?P<url>http[s]?://[^' + notInside + ']*?[^' + notAtEnd \
				+ '](?=[' + notAtEnd+ ']*\'\')|http[s]?://[^' + notInside \
				+ ']*[^' + notAtEnd + '])'

		if withoutBracketed:
			regex = r'(?<!\[)' + regex
		elif onlyBracketed:
			regex = r'\[' + regex
		linkR = re.compile(regex)
		return linkR

	def get_links(self, regex, text):
		nestedTemplateR = re.compile(r'{{([^}]*?){{(.*?)}}(.*?)}}')
		while nestedTemplateR.search(text):
			text = nestedTemplateR.sub(r'{{\1 \2 \3}}', text)

		# Then blow up the templates with spaces so that the | and }} will not be regarded as part of the link:.
		templateWithParamsR = re.compile(r'{{([^}]*?[^ ])\|([^ ][^}]*?)}}', re.DOTALL)
		while templateWithParamsR.search(text):
			text = templateWithParamsR.sub(r'{{ \1 | \2 }}', text)

		for m in regex.finditer(text):
			yield m.group('url')

	def get_ignorelist(self):
		try:
			text = wikitools.Page(wiki, IGNORE_LIST).getWikiText()
		except Exception:
			self.log.add('Could not read ignore list')
			return []
		self.log.add('Fetched ignore list')

		listRE = re.compile(r'== URLs ==\n(.+)', re.DOTALL)
		text = listRE.search(text).group(1)

		urlRE = re.compile(r'\*\s*(.+)')
		urls = urlRE.findall(text)

		return [strip_slashes(url) for url in urls]

	def is_suspicious_link(self, url):
		s_urls = ['wiki.tf2.com', 'wiki.teamfortress.com', 'wiki.tf', 'pastie', 'paste']

		for s_url in s_urls:
			if s_url in url:
				return True
		return False

	def run(self):
		for page in self.pages:
			self.check_links_in(page)

	def check_url(self, page, url, lock):
		self.log.add('Processing ' + url)

		lock.acquire()
		if url in self.data:
			self.data[url]['pages'] += [page]
			lock.release()
			return None
		if url in self.links:
			lock.release()
			return None
		else:
			self.links.append(url)
			lock.release()

		if self.is_suspicious_link(url):
			lock.acquire()
			if url in self.suspicious:
				self.suspicious[url]['pages'] += [page]
			else:
				self.suspicious[url] = {'pages': [page]}
			lock.release()
			return None

		linkChecker = LinkChecker(url)
		ok, message = linkChecker.check()

		if not ok:
			self.log.add('Found dead link: ' + url)
			lock.acquire()
			self.data[url] = {'message': message, 'pages': [page]}
			lock.release()

	def check_links_in(self, page):
		try:
			text = wikitools.Page(wiki, page).getWikiText()
		except Exception:
			self.log.add('Could not get text from ' + page)
			return None
		linkRegex = self.return_link_regex()

		for url in self.get_links(linkRegex, text):
			if strip_slashes(url) in self.ignorelist:
				self.log.add('url in ignore list: ' + url)
			else:
				self.pool.add_task(self.check_url, page, url, self.lock)

	def return_data(self):
		return self.data, self.suspicious

def is_image(url):
	imageRE = re.compile(r".(jpg|jpeg|png|gif)$")
	if imageRE.match(url):
		return True
	return False

def save(data, suspicious):
	f = open('deadlinks.txt', 'wb')

	output = '== Dead or incorrectly behaving links ==\n'
	for url in data:
		output += '* {0} ({1})\n'.format(url, data[url]['message'])
		for page in data[url]['pages']:
			output += '** [[{0}]]\n'.format(page.encode('utf-8'))
	output += '\n== Suspicious links ==\n'
	for url in suspicious:
		if is_image(url):
			output += '* [{0}]\n'.format(url)
		else:
			output += '* {0}\n'.format(url)
		for page in suspicious[url]['pages']:
			output += '** [[{0}]]\n'.format(page.encode('utf-8'))

	f.write(output)
	f.close()

	wikitools.Page(wiki, OUTPUT_PAGE).edit(output, summary=u'Updated', minor=True, bot=False, skipmd5=True, createonly=False, timeout=60)

def run():
	pages = get_all_articles()
	pool = ThreadPool(NUM_THREADS)
	linkbot = WeblinkCheckerRobot(pool, pages)
	linkbot.run()
	pool.wait_completion()

	data, suspicious = linkbot.return_data()
	save(data, suspicious)


if __name__ == '__main__':
	run()
