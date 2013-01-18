__module_name__ = "Wiki spam blocker"
__module_version__ = "1.0"
__module_description__ = "Blocks wiki spammers and deletes pages created"

import xchat
import wikitools
import threading

USERNAME = ''
PASSWORD = ''

WIKI_API = r'http://wiki.tf2.com/w/api.php'

wiki = wikitools.Wiki(WIKI_API)
wiki.login(username=USERNAME, password=PASSWORD)

def block_user(user):
	user.block(reason='Spamming links to external sites', expiry=False, nocreate=True, autoblock=True)

def get_user_edits(user):
	params = {
		'action': 'query',
		'list': 'usercontribs',
		'ucuser': 'User:' + user,
		'uclimit': '100',
		'ucprop': 'title|flags',
		}

	req = wikitools.api.APIRequest(wiki, params)
	res = req.query(querycontinue=True)

	return res['query']['usercontribs']

def get_created_pages(contribs):
	titles = []
	for edit in contribs:
		if u'new' in edit:
			titles.append(edit['title'])
	return titles

def delete_pages(pages):
	for page in pages:
		wikitools.Page(wiki, page).delete('Spam')

def activate_killer(word, word_eol, userdata):
	thread = KillerThread()
	thread.kill_spammer(word, word_eol, userdata)


class KillerThread(threading.Thread):

	def kill_spammer(self, word, word_eol, userdata):
		if len(word) < 2:
			xchat.prnt('Error: username was not supplied')
			return

		username = word_eol[1]
		user = wikitools.User(wiki, username)
		if not user.isBlocked():
			block_user(user)
			xchat.prnt('User:' + username + ' has been blocked')

			edits = get_user_edits(username)
			pagescreated = get_created_pages(edits)
			delete_pages(pagescreated)
		else:
			xchat.prnt('User:' + username + ' has already been blocked')


xchat.hook_command('block', activate_killer)
