import re, urllib, urllib2
languages = 'en, ar, cs, es, da, de, fi, fr, hu, it, ja, ko, nl, no, pl, pt, pt-br, ro, ru, sv, tr, zh-hans, zh-hant'.split(', ')
full_languages = 'English, Arabic, Czech, Spanish, Danish, German, Finnish, French, Hungarian, Italian, Japanese, Korean, Dutch, Norwegian, Polish, Portuguese, Portuguese (Brazil), Romanian, Russian, Swedish, Turkish, Chinese (Simplified), Chinese (Traditinal)'.split(', ')
exts = 'png, jpg, jpeg, mp3, wav, txt, gif'.split(', ')

step = 500
output = []
i = 0
while (True):
	data = urllib2.urlopen("https://wiki.teamfortress.com/wiki/Special:UnusedFiles?limit={step}&offset={i}".format(step=step, i=i)).read()
	m = re.search('There are no results for this report\.', data)
	if m is not None:
		break
	for m in re.finditer('data-url="(.*?)"', data):
		file = re.search('(.*)/(1024px-|)(.*)\.(.*)', m.group(1))
		lang = file.group(3).split('_')[-1]
		if lang in languages:
			lang = languages.index(lang)
		else:
			lang = 0
		output.append([file.group(3), urllib.unquote(file.group(4)).lower(), lang])
	i += step
	print i
output.sort(key=lambda s: (exts.index(s[1]), s[2], s[0]))
f = open('unused_files.txt', 'wb')
f.write('{{{{DISPLAYTITLE:{n} unused files}}}}\n'.format(n=len(output)))
type = ''
lang = -1
for o in output:
	if o[0][:5] == 'User_':
		output.remove(o)
		continue
	if o[0][:9] == 'Backpack_':
		output.remove(o)
		continue
	if o[0][:4] == 'BLU_':
		output.remove(o)
		continue
	if o[0][:10] == 'Item_icon_':
		output.remove(o)
		continue
	if type != o[1].upper():
		type = o[1].upper()
		f.write('== {type} ==\n'.format(type=type))
		lang = -1
	if lang != o[2]:
		lang = o[2]
		f.write('=== {lang} ===\n'.format(lang=full_languages[lang]))
	f.write('*[[Special:WhatLinksHere/File:{lname}|{name}]]\n'.format(lname=o[0]+'.'+o[1], name=urllib.unquote(o[0])+'.'+o[1]))
f.close()
print 'Done, output written to unused_files.txt'