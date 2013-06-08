# -*- coding: utf-8 -*-
import wikitools

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
dupes = {}

for image in images:
	if 'duplicatefiles' in images[image]:
		filename = images[image]['title']
		dupefiles = [u'File:'+_file['name'] for _file in images[image]['duplicatefiles']]
		dupes[filename] = dupefiles

output = ''
for dupe in dupes:
	output += '<gallery>\n'
	output += '{0}|{1}\n'.format(dupe, dupe[5:])
	for duplicate in dupes[dupe]:
		output += '{0}|{1}\n'.format(duplicate, duplicate[5:])
	output += '</gallery>\n'

with open('Wiki_dupe_files_output.txt', 'wb') as f:
	f.write(output)