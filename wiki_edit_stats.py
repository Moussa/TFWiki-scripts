import urllib2, json, time, locale
from datetime import datetime
from datetime import date
from operator import itemgetter
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
	if aufrom:
		url = wikiAddress + r'&aufrom=' + aufrom
		result = json.loads(urllib2.urlopen(url.encode('utf-8')).read())
	else:
		result = json.loads(urllib2.urlopen(wikiAddress).read())
	list = result['query']['allusers']
	usersList += list
	print 'User count:', str(len(usersList))
	if 'query-continue' in result:
		populate_list(aufrom=result['query-continue']['allusers']['aufrom'])
	else:
		return 1

def userEditCount(nlower, nupper=None):
	count = 0
	for user in sortedList:
		if nupper is None:
			if user['editcount'] >= nlower:
				count += 1
		else:
			if nlower <= user['editcount'] and user['editcount'] <= nupper:
				count += 1
	return count

def addTableRow(nlower, nupper=None):
	if nupper is None:
		return """\n|-
| {nlower}+
| {{{{Chart bar|{count}|max={max}}}}}
| {percentage}%""".format(nlower = nlower,
						 count = userEditCount(nlower),
						 max = len(usersList),
						 percentage = str('%.2f' % (100 * float(userEditCount(nlower))/float(len(usersList))))
						 )
	else:
		return """\n|-
| {nlower} - {nupper}
| {{{{Chart bar|{count}|max={max}}}}}
| {percentage}%""".format(nlower = nlower,
						 nupper = nupper,
						 count = userEditCount(nlower, nupper),
						 max = len(usersList),
						 percentage = str('%.2f' % (100 * float(userEditCount(nlower, nupper))/float(len(usersList))))
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
	timeRange = [[0]*12 for i in range(NUMYEARS)] #[year][month]
	for user in timeSortedList:
		time = user['registration']
		timeRange[int(time[:4])-2010][int(time[5:7])-1] += 1 # 2013-05 -> 3, 4
	runningTotal = 0
	output = ""
	for year in range(NUMYEARS):
		for month in range(1,12):
			if year == date.today().year and month == date.today().month:
				continue # In current month, data would be incomplete
			numUsers = timeRange[year][month-1]
			if numUsers == 0:
				continue # Time segment has no data, just skip.
			runningTotal += numUsers
			output += """\n|-
| <span style="display:none;">{year}{month}</span>{monthName} {year}
| {{{{Chart bar|{numUsers}|max=3500}}}}
| {total}""".format(numUsers = numUsers,
			 month = month,
			 monthName = monthName(month),
			 year = year+2010,
			 total = runningTotal)
	return output

populate_list()

sortedList = sorted(usersList, key=itemgetter('editcount'), reverse=True)
timeSortedList = sorted(usersList, key=itemgetter('registration'))

outputString = """User edits statistics. Data accurate as of {0} (GMT). Further stats available at [http://stats.wiki.tf/wiki/tf stats.wiki.tf]
;Note<nowiki>:</nowiki> All data excludes registered users with no edits.""".format(time.strftime(r'%H:%M, %d %B %Y', time.gmtime()))

outputString += """\n\n== Edit count distribution ==
{| class="wikitable grid sortable plainlinks" style="text-align: center"
! class="header" width="30%" | Number of edits
! class="header" width="50%" | Users
! class="header" width="20%" | Percentage of users"""
print("""Adding percentage breakdown""")
outputString += addTableRow(1, 10)
outputString += addTableRow(11, 100)
outputString += addTableRow(101, 1000)
outputString += addTableRow(1001, 5000)
outputString += addTableRow(5001)
outputString += """\n|}"""
print("""Adding joins per month""")
outputString += """\n\n== User signups ==
{| class="wikitable grid sortable plainlinks" style="text-align:center"
! class="header" width="30%" | Date
! class="header" width="50%" | Signups
! class="header" width="20%" | Total number of users"""
outputString += addTimeData(timeSortedList)
outputString += "\n|}"
print("""Adding top 100 editors list""")
outputString += """\n\n== Top editors list ==
Limited to the top 100.
Bots are in ''italics''.

{{| class="wikitable grid sortable"
! class="header" | #
! class="header" | User
! class="header" | Edit count
! class="header" | Edits per day
! class="header" | Registration date""".format(time.strftime(r'%H:%M, %d %B %Y', time.gmtime()))

n = 1
timenow = datetime.now()
for user in sortedList[:100]:
	username = user['name']
	usereditcount = user['editcount']
	userregistration = user['registration']
	if username in usernameSubs:
		username = usernameSubs[username]
	userlink = 'User:'+username
	if 'BOT' in username:
		username = "\'\'"+username+"\'\'"
	userstarttime = datetime.strptime(userregistration, r'%Y-%m-%dT%H:%M:%SZ')
	timedelta = timenow - userstarttime
	editsperday = ('%.2f' % (float(usereditcount)/float(timedelta.days)))
	outputString += """\n|-
| {n} || [[{userlink}|{username}]] || {editcount} || {editday} || <span style="display:none;">{sortabledate}</span>{date}""".format(
			n = str(n),
			userlink = userlink,
			username = username,
			editcount = locale.format('%d', usereditcount, grouping=True),
			editday = str(editsperday),
			sortabledate = time.strftime(r'%Y-%m-%d %H:%M:00', time.strptime(userregistration, r'%Y-%m-%dT%H:%M:%SZ')),
			date = time.strftime(r'%H:%M, %d %B %Y', time.strptime(userregistration, r'%Y-%m-%dT%H:%M:%SZ'))
			)
	n += 1
outputString += "\n|}"

file = open(r'edit_count_table.txt', 'wb')
file.write(outputString)
print 'Article written to edit_count_table.txt'
file.close()
