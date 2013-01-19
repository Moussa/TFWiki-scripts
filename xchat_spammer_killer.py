__module_name__ = "Wiki Spam Killer"
__module_version__ = "1.1"
__module_description__ = "Blocks wiki spammers and deletes pages created"

import threading, sys, datetime, pytz
import xchat
import wikitools


USERNAME = ''
PASSWORD = ''

WIKI_API = r'http://wiki.tf2.com/w/api.php'


class KillerThread(threading.Thread):
	def __init__(self):
		xchat.prnt('Wiki Spam Killer started')
		self.wiki = wikitools.Wiki(WIKI_API)
		self.loggedin = False

	def login(self):
		if self.wiki.login(username=USERNAME, password=PASSWORD):
			self.loggedin = True
			xchat.prnt('Succesfully logged into wiki')
		else:
			xchat.prnt('Error: failed to log into wiki. Please reload module with correct login details')

	def block_user(self, user):
		user.block(reason='Spamming links to external sites', expiry=False, nocreate=True, autoblock=True)

	def get_user_edits(self, user):
		params = {
			'action': 'query',
			'list': 'usercontribs',
			'ucuser': 'User:' + user,
			'uclimit': '100',
			'ucprop': 'title|flags',
			}

		req = wikitools.api.APIRequest(self.wiki, params)
		res = req.query(querycontinue=True)

		return res['query']['usercontribs']

	def get_created_pages(self, contribs):
		titles = []
		for edit in contribs:
			if u'new' in edit:
				titles.append(edit['title'])
		return titles

	def delete_pages(self, pages):
		for page in pages:
			wikitools.Page(self.wiki, page).delete('Spam')

	def is_old_user(self, user):
		now = datetime.datetime.now(pytz.utc)
		age = now - user.registration
		return age.days > 1

	def kill_spammer(self, word, word_eol, userdata):
		if not self.loggedin:
			xchat.prnt('Error: please reload module with correct login details')
			return None
		if len(word) < 2:
			xchat.prnt('Error: username was not supplied')
			return None

		username = word_eol[1]
		user = wikitools.User(self.wiki, username)
		if self.is_old_user(user):
			xchat.prnt('User:' + username + ' is > 1 day old. Backing off.')
		elif not user.isBlocked():
			self.block_user(user)
			xchat.prnt('User:' + username + ' has been blocked')

			edits = self.get_user_edits(username)
			pagescreated = self.get_created_pages(edits)
			self.delete_pages(pagescreated)
		else:
			xchat.prnt('User:' + username + ' has already been blocked')


def kill_spammer(word, word_eol, userdata):
	thread.kill_spammer(word, word_eol, userdata)

thread = KillerThread()
thread.login()

xchat.hook_command('block', kill_spammer)
