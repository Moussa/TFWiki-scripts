# -*- coding: utf-8 -*-
import os
import re

SCRIPTS_LOCATION = r'F:\Steam\steamapps\common\portal 2\portal2\resource'

tokenRE = re.compile(r'\"(?P<token>.[^\"]+)\"[\t\s]+\"(?P<transstring>.[^\"]+)\"[\n\r][\s\t]*\"\[english\](?P=token)\"[\t\s]+\"(?P<origstring>.[^\"]+)\"', re.DOTALL)
lineWithCaptionRE = re.compile(r'(\<.[^>]+\>){1,2}([\w\d\s]+:\s)?(?P<line>.+)', re.DOTALL)
escapeCharRE = re.compile(r"\||\*|''+|\[\[+|~")

portal2scripts = {
	'cz': 'subtitles_czech.txt',
	'da': 'subtitles_danish.txt',
	'nl': 'subtitles_dutch.txt',
	'fi': 'subtitles_finnish.txt',
	'fr': 'subtitles_french.txt',
	'de': 'subtitles_german.txt',
	'hu': 'subtitles_hungarian.txt',
	'it': 'subtitles_italian.txt',
	'ja': 'subtitles_japanese.txt',
	'ko': 'subtitles_korean.txt',
	'ka': 'subtitles_koreana.txt',
	'no': 'subtitles_norwegian.txt',
	'pl': 'subtitles_polish.txt',
	'pt': 'subtitles_portuguese.txt',
	'ro': 'subtitles_romanian.txt',
	'ru': 'subtitles_russian.txt',
	'zh-hans': 'subtitles_schinese.txt',
	'es': 'subtitles_spanish.txt',
	'sw': 'subtitles_swedish.txt',
	'zh-hant': 'subtitles_tchinese.txt',
	'th': 'subtitles_thai.txt',
	'tu': 'subtitles_turkish.txt'
}

characters = {
	'cavejohnson': 'Cave Johnson',
	'glados': 'GLaDOS',
	'sphere03': 'Wheatley',
	'core03': 'Adventure core',
	'core02': 'Fact core',
	'core01': 'Space core',
	'turret': 'Turret',
	'npc_floorturret': 'Floor Turret',
	'turret': 'Defective Turret',
	'announcer': 'Announcer'
}


def clean_string(string):
	res = lineWithCaptionRE.match(string)
	if res:
		clean_string = res.group('line').strip()
	else:
		clean_string = string.strip()

	return escape_string(clean_string)

def escape_string(string):
	if escapeCharRE.search(string):
		return '<nowiki>{0}</nowiki>'.format(string)
	return string

trans_dict = {}
for lang in portal2scripts:
	with open(SCRIPTS_LOCATION + os.sep + portal2scripts[lang], 'rb') as f:
		content = unicode(f.read(), "utf-16").encode("utf-8")
		matches = tokenRE.findall(content)
		for match in matches:
			token, transstring, origstring = match
			if token not in trans_dict:
				trans_dict[token] = {'en': origstring, lang: transstring}
			else:
				trans_dict[token][lang] = transstring

output = {}
for token in sorted(trans_dict.keys()):
	# forget those commentary lines
	if token.startswith('#commentary') or token.startswith('Commentary'):
		continue
	character, filename = tuple(token.split('.', 1))
	character = characters[character]
	filename = filename.replace('_', ' ').lower()
	strings = trans_dict[token]

	dictionary_entry = '\n\n{filename}:'.format(character=character.lower(), filename=filename)
	dictionary_entry += '\n  en: {string}'.format(string=clean_string(strings['en']))

	langs = strings.keys()
	langs.remove('en')
	for lang in sorted(langs):
		dictionary_entry += '\n  {lang}: {string}'.format(lang=lang, string=clean_string(strings[lang]))

	output[character] = output.get(character, '') + dictionary_entry

with open('portal_voice_lines.txt', 'wb') as f:
	for character in sorted(output.keys()):
		f.write('\n\n=== {0} ==='.format(character))
		f.write('\n\n<!--')
		f.write(output[character])
		f.write('\n\n-->')
