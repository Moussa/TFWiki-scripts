# -*- coding: utf-8 -*-
import wikitools

WIKI_API = 'http://wiki.tf2.com/w/api.php'
wiki = wikitools.Wiki(WIKI_API)

def get_images(wiki):
	params = {'action': 'query',
              'generator': 'allimages',
              'prop': 'duplicatefiles',
              'gailimit': 500
              }

	req = wikitools.api.APIRequest(wiki, params)
	res = req.query(querycontinue=True)

	return res['query']['pages']


images = get_images(wiki)
seen = []
dupes = {}

for _image in images:
	image = images[_image]
	filename = image['title'].replace('_', ' ')
	if 'duplicatefiles' in image and filename not in seen:
		dupefiles = ['File:'+_file['name'].replace('_', ' ') for _file in image['duplicatefiles']]
		for _file in dupefiles:
			if _file not in seen:
				seen.append(_file)
		dupes[filename] = dupefiles
		seen.append(filename)

output = ''
for dupe in sorted(dupes):
	output += '<gallery>\n'
	output += '{0}|{1}\n'.format(dupe, dupe[5:])
	for duplicate in dupes[dupe]:
		output += '{0}|{1}\n'.format(duplicate, duplicate[5:])
	output += '</gallery>\n'

with open('wiki_dupe_files_output.txt', 'wb') as f:
	f.write(output)