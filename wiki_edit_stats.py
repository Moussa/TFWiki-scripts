import locale
from urllib2 import urlopen
from datetime import date, datetime
from json import loads
from operator import itemgetter
from time import strftime, strptime, gmtime
from urllib import quote
global NUMYEARS
NUMYEARS = date.today().year-2010 + 1 # 2014 - 2010 + 1 = 5 (years)

locale.setlocale(locale.LC_ALL, '')

wikiAddress = r'http://wiki.teamfortress.com/w/api.php?action=query&list=allusers&auprop=editcount|registration&auwitheditsonly&aulimit=500&format=json'
usernameSubs = {'Ohyeahcrucz': 'Cructo',
				'I-ghost': 'i-ghost',
				'Darkid': 'darkid'
				}

usersList = []

def populate_list(aufrom=None):
	global usersList
	url = wikiAddress
	if aufrom:
		url += r'&aufrom=' + aufrom
	result = loads(urlopen(url.encode('utf-8')).read())
	usersList += result['query']['allusers']
	print 'User count:', len(usersList)
	if 'query-continue' in result:
		populate_list(aufrom=result['query-continue']['allusers']['aufrom'])

def userEditCount(nlower, nupper=None):
	count = 0
	for user in sortedList:
		if nlower <= user['editcount']:
			if nupper == None or user['editcount'] <= nupper:
				count += 1
	return count

def addTableRow(nlower, nupper=None):
	print "Adding users with edit count", nlower, "-", nupper
	count = userEditCount(nlower, nupper)
	if nupper is None:
		return """|-
| {nlower}+
| {{{{Chart bar|{count}|max={max}}}}}
| {percentage}%""".format(nlower = nlower,
						 count = count,
						 max = len(usersList),
						 percentage = round(100 * float(count) / len(usersList), 2)
						 )
	else:
		return """|-
| {nlower} - {nupper}
| {{{{Chart bar|{count}|max={max}}}}}
| {percentage}%""".format(nlower = nlower,
						 nupper = nupper,
						 count = count,
						 max = len(usersList),
						 percentage = round(100 * float(count) / len(usersList), 2)
						 )

def monthName(n):
	return {1: "January",
		2: "February",
		3: "March",
		4: "April",
		5: "May",
		6: "June",
		7: "July",
		8: "August",
		9: "September",
		10: "October",
		11: "November",
		12: "December",
		}[n]

def addTimeData(timeSortedList):
	print "Adding user signups"
	timeRange = [[0]*12 for i in range(NUMYEARS)] # timeRange[year][month]
	for user in timeSortedList:
		time = user['registration']
		timeRange[int(time[:4])-2010][int(time[5:7])-1] += 1 # 2013-05 -> year 3, month 4
	runningTotal = 0
	output = ""
	for year in range(2010, 2010+NUMYEARS):
		for month in range(1, 13):
			if year == date.today().year and month == date.today().month:
				break # We've reached the present, so current data is incorrect and future data is blank.
			numUsers = timeRange[year-2010][month-1]
			if numUsers == 0:
				continue # No data for given time period
			runningTotal += numUsers
			output += """|-
| data-sort-value="{year}-{month}" | {monthName} {year}
| {{{{Chart bar|{numUsers}|max=3500}}}}
| {total}\n""".format(numUsers = numUsers,
			 month = "%02d" % month,
			 monthName = monthName(month),
			 year = year,
			 total = runningTotal)
	return output

def addTopUsers(sortedList, count):
	print "Adding top", count, "users"
	output = ""
	for n in range(count):
		user = sortedList[n]
		username = user['name']
		usereditcount = user['editcount']
		userregistration = user['registration']
		wikifi_link = 'http://stats.wiki.tf/user/tf/'+quote(username)
		userlink = 'User:'+username
		if username in usernameSubs:
			username = usernameSubs[username]
		# if 'BOT' in username:
		# 	username = "''"+username+"''"
		userstarttime = strptime(userregistration, r'%Y-%m-%dT%H:%M:%SZ')
		timedelta = (datetime.now() - userstarttime).days
		editsperday = round(float(usereditcount) / timedelta, 2)
		output += """|-
	| {place} || [[{userlink}|{username}]] || {editcount} || {editday} || data-sort-value="{sortabledate}" | {date} || [{wikifi_link} {username}]\n""".format(
				place = n+1, # List is indexed 0-99, editors are indexed 1-100
				userlink = userlink,
				username = username,
				editcount = locale.format('%d', usereditcount, grouping=True),
				editday = str(editsperday),
				sortabledate = strftime(r'%Y-%m-%d %H:%M:00', strptime(userregistration, r'%Y-%m-%dT%H:%M:%SZ')),
				date = strftime(r'%H:%M, %d %B %Y', strptime(userregistration, r'%Y-%m-%dT%H:%M:%SZ')),
				wikifi_link = wikifi_link
				)
	return output


# Main code starts here.

populate_list()

sortedList = sorted(usersList, key=itemgetter('editcount'), reverse=True)
timeSortedList = sorted(usersList, key=itemgetter('registration'))

file = open(r'edit_count_table.txt', 'wb')
file.write("""User edits statistics. Data accurate as of """ + str(strftime(r'%H:%M, %d %B %Y', gmtime())) + """ (GMT). Further stats available at [http://stats.wiki.tf/wiki/tf stats.wiki.tf].
;Note: All data excludes registered users with no edits.

== Edit count distribution ==
{| class="wikitable grid sortable plainlinks" style="text-align: center"
! class="header" width="30%" | Number of edits
! class="header" width="50%" | Users
! class="header" width="20%" | Percentage of users
""" + addTableRow(1, 10) + """
""" + addTableRow(11, 100) + """
""" + addTableRow(101, 1000) + """
""" + addTableRow(1001, 5000) + """
""" + addTableRow(5001) + """
|}

== User signups ==
{| class="wikitable grid sortable plainlinks" style="text-align:center"
! class="header" width="30%" | Date
! class="header" width="50%" | Signups
! class="header" width="20%" | Total number of users
""" + addTimeData(timeSortedList) + """
|}

== Top 100 editors ==
{| class="wikitable grid sortable"
! class="header" | #
! class="header" | User
! class="header" | Edit count
! class="header" | Edits per day
! class="header" | Registration date
! class="header" | Wiki-fi link
""" + addTopUsers(sortedList, 100) + """
|}""")

print("Article written to edit_count_table.txt")
file.close()
