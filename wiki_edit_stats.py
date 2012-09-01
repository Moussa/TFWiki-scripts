# Generates the user edit stats article found on the wiki.

import urllib, urllib2, json, time, locale
from datetime import datetime
from datetime import timedelta
from operator import itemgetter

locale.setlocale(locale.LC_ALL, '')

wikiAddress = r'http://wiki.teamfortress.com/w/api.php'
usernameSubs = {'Ohyeahcrucz': 'Cructo',
				'I-ghost': 'i-ghost'
				}
usersList = []

def populate_list(aufrom=None):
	global usersList
	if aufrom:
		result = json.loads(urllib2.urlopen(wikiAddress + r'?action=query&list=allusers&auprop=editcount|registration&auwitheditsonly&aulimit=500&format=json&aufrom=' + aufrom).read())
	else:
		result = json.loads(urllib2.urlopen(wikiAddress + r'?action=query&list=allusers&auprop=editcount|registration&auwitheditsonly&aulimit=500&format=json').read())
	data = result['query']['allusers']
	usersList += data
	print 'User count:', str(len(usersList))
	if 'query-continue' in result:
		populate_list(aufrom=result['query-continue']['allusers']['aufrom'])
	else:
		return 1

def get_edits_count_period(user, daysago):
	loop = True
	ucstart = None
	count = 0
	while loop:
		if ucstart:
			content = urllib2.urlopen(wikiAddress + r'?action=query&list=usercontribs&ucuser=%s&ucend=%s&ucstart=%s&uclimit=500&format=json' % (user, daysago, ucstart)).read()
			content.decode('ascii')
			result = json.loads(content)
		else:
			content = urllib2.urlopen(wikiAddress + r'?action=query&list=usercontribs&ucuser=%s&ucend=%s&uclimit=500&format=json' % (user, daysago)).read()
			content.decode('ascii')
			result = json.loads(content)
		count += len(result['query']['usercontribs'])
		if 'query-continue' in result:
			ucstart = result['query-continue']['usercontribs']['ucstart']
		else:
			loop = False
	return count

def get_user_edit_count(nlower, nupper=None):
	count = 0
	for user in sortedList:
		if nupper is None:
			if user['editcount'] >= nlower:
				count += 1
		else:
			if nlower <= user['editcount'] and user['editcount'] <= nupper:
				count += 1
	return count

def add_table_row(column1, column3, count, max):
	return """\n|-
| {column1}
| {{{{Chart bar|{count}|max={max}}}}}
| {column3}""".format(column1 = column1,
					  count = count,
					  max = max,
					  column3 = column3
					  )

def return_table(userlist, timestart=None, recentedits=False):
	tablestring = """{{| class="wikitable grid sortable"
|-
! class="header" | #
! class="header" | User
! class="header" | Edit count
! class="header" | Edits per day
! class="header" | Registration date
|-""".format(time.strftime(r'%H:%M, %d %B %Y', time.gmtime()))

	n = 1
	timenow = datetime.now()
	for user in userlist:
		username = user['name'].encode('utf-8')
		if recentedits:
			usereditcount = user['editcountrecent']
		else:
			usereditcount = user['editcount']
		userregistration = user['registration']
		if username in usernameSubs:
			username = usernameSubs[username]
		if recentedits:
			userstarttime = datetime.strptime(timestart, r'%Y-%m-%dT%H:%M:%SZ')
		else:
			userstarttime = datetime.strptime(userregistration, r'%Y-%m-%dT%H:%M:%SZ')
		timedelta = timenow - userstarttime
		editsperday = ('%.2f' % (float(usereditcount)/float(timedelta.days)))

		tablestring += '\n' + """| {n} || [[User:{username}|{username}]] || {editcount} || {editday} || <span style="display:none;">{sortabledate}</span>{date}
|-""".format(n = str(n),
			 username = username,
			 editcount = locale.format('%d', usereditcount, grouping=True),
			 editday = str(editsperday),
			 sortabledate = time.strftime(r'%Y-%m-%d %H:%M:00', time.strptime(userregistration, r'%Y-%m-%dT%H:%M:%SZ')),
			 date = time.strftime(r'%H:%M, %d %B %Y', time.strptime(userregistration, r'%Y-%m-%dT%H:%M:%SZ'))
			 )
		n += 1
	tablestring += '\n|}'
	return tablestring

populate_list()
# Get rid of duplicate user entries because of MediaWiki API bug
print 'Removing duplicate users from list'
knowndata = set()
newlist = []
for entry in usersList:
	user = entry['name']
	if user in knowndata: continue
	newlist.append(entry)
	knowndata.add(user)
usersList[:] = newlist

sortedList = sorted(usersList, key=itemgetter('editcount'), reverse=True)

# Calculate top editors in last month
count = 0
total = len(sortedList)
editcountlist = []
timendaysago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%dT%H:%M:%SZ')
for user in sortedList:
	username = user['name'].encode('utf-8')
	count += 1
	if len(editcountlist) < 50:
		print 'Processing user {0}/{1}, {2}'.format(str(count), str(total), username)
		user[u'editcountrecent'] = get_edits_count_period(urllib.quote(username), timendaysago)
		if user['editcountrecent'] is not None:
			editcountlist.append(int(user['editcountrecent']))
	else:
		if int(user['editcount']) < min(editcountlist):
			# Reached point where rest of users have a total edit count < the top 50 editors
			break
		else:
			user[u'editcountrecent'] = get_edits_count_period(urllib.quote(username), timendaysago)
			if user['editcountrecent'] is not None and user['editcountrecent'] > min(editcountlist):
				print 'Processing user {0}/{1}, {2}'.format(str(count), str(total), username)
				editcountlist.remove(min(editcountlist))
				editcountlist.append(int(user['editcountrecent']))
			else:
				print 'Processing user {0}/{1}, {2} < top 50 editors'.format(str(count), str(total), username)

# Necessary because of users skipped in loop
def return_user_key_value(user):
	if user.has_key('editcountrecent'):
		return user['editcountrecent']
	else:
		return 0
sortedRecentList = sorted(sortedList, key=return_user_key_value, reverse=True)


### Start article ###
outputString = """User edit statistics. Data accurate as of {0} (GMT)
;Note<nowiki>:</nowiki> All data excludes registered users with no edits""".format(time.strftime(r'%H:%M, %d %B %Y', time.gmtime()))

## Edit count distribution section ##
outputString += """\n\n== Edit count distribution ==
{| class="wikitable grid sortable plainlinks" style="text-align: center;width=50%;"
|-
! class="header" width="30%" | Number of edits
! class="header" width="50%" | Users
! class="header" width="20%" | Percentage of users"""

outputString += add_table_row('1 - 10', str('%.2f' % (100 * float(get_user_edit_count(1, 10))/float(len(usersList)))) + r'%', get_user_edit_count(1, 10), len(usersList))
outputString += add_table_row('11 - 100', str('%.2f' % (100 * float(get_user_edit_count(11, 100))/float(len(usersList)))) + r'%', get_user_edit_count(11, 100), len(usersList))
outputString += add_table_row('101 - 1000', str('%.2f' % (100 * float(get_user_edit_count(101, 1000))/float(len(usersList)))) + r'%', get_user_edit_count(101, 1000), len(usersList))
outputString += add_table_row('1001 - 5000', str('%.2f' % (100 * float(get_user_edit_count(1001, 5000))/float(len(usersList)))) + r'%', get_user_edit_count(1001, 5000), len(usersList))
outputString += add_table_row('5001+', str('%.2f' % (100 * float(get_user_edit_count(5001))/float(len(usersList)))) + r'%', get_user_edit_count(5001), len(usersList))
outputString += """\n|}"""

## User signups section ##
print 'Processing signups table'
outputString += """\n\n== User signups ==
{| class="wikitable grid sortable plainlinks" style="text-align: center;width=50%;"
|-
! class="header" width="30%" | Period
! class="header" width="50%" | Signups
! class="header" width="20%" | Total number of users"""

startdate = datetime(2010, 6, 1)
enddate = datetime(2010, 7, 1)
totalusercount = 0
while startdate < datetime.now():
	count = 0
	for user in sortedList:
		usersignup = datetime.strptime(user['registration'], r'%Y-%m-%dT%H:%M:%SZ') 
		if startdate <= usersignup and usersignup < enddate:
			count += 1
	totalusercount += count
	outputString += add_table_row('<span style="display:none;">{0}</span>{1}'.format(startdate.strftime(r'%y%m'), startdate.strftime(r'%B %Y')), locale.format('%d', totalusercount, grouping=True), count, 3500)
	startdate = enddate
	year, month, day = enddate.date().timetuple()[:3]
	enddate = datetime(year + (month / 12), ((month + 1) % 12) or 12, day)
outputString += """\n|}"""

## Top editors section ##
outputString += """\n\n== Top editors of all time ==
Limited to the top 100.\n\n"""

outputString += return_table(sortedList[:100])

## Top editors in last 30 days section ##
outputString += """\n\n== Top editors in the last 30 days ==
Limited to the top 50.\n\n"""

outputString += return_table(sortedRecentList[:50], timendaysago, True)

file = open(r'wiki_editstats_article.txt', 'wb')
file.write(outputString)

print 'All done'
print 'Article written to wiki_editstats_article.txt'