# -*- coding: utf-8 -*-
# A script to upload updated tf_*.txt files after a patch to the wiki

import re, os
import wikitools
import subprocess
import getpass

statusRe = re.compile(r'^(\w)\s+(.+)')

content = r"""<!-- This page is updated by a bot. Changes made to it will likely be lost the next time it edits. -->
== Recent changes ==
{{tf diff|p=%s}}
== File info ==
'''Note''': this encoding of this file has been changed from UCS-2 Little Endian (UTF-16) to UTF-8 (without BOM) to reduce filesize. The content of the file still matches the original version from {{code|root\tf\resource}}.
== Licensing ==
{{Externally linked}}
{{ExtractTF2}}
[[Category:Text files]]
[[Category:Localization files]]"""

def update_lang_files(wikiUsername, wikiPassword, patchTitle, gitRepo, wikiApi = r'http://wiki.tf2.com/w/api.php'):
	files = []
	p = subprocess.Popen(['git', 'status', '--short'], shell=True, stdout=subprocess.PIPE, cwd=gitRepo)
	filesChanged, err = p.communicate()
	filesChanged = [line.strip() for line in filesChanged.split('\n')]
	for file_ in filesChanged:
		filename = re.search(statusRe, file_).group(2)
		filename = os.path.split(filename)[1]
		if filename.startswith('tf_') and filename.endswith('.txt'):
			files.append(filename)

	wiki = wikitools.wiki.Wiki(wikiApi)
	wiki.login(wikiUsername, wikiPassword)
	for file_ in files:
		success = False
		n = 0
		while n < 5 and not success:
			try:
				loc_file = wikitools.wikifile.File(wiki=wiki, title=u'File:' + file_)
				loc_file.upload(fileobj=open(gitRepo + os.sep + r'tf\resource' + os.sep + file_, "rb"), ignorewarnings=True, comment=u'Uploaded new revision of %s for [[:%s]].' % (file_, patchTitle))
				wikitools.page.Page(wiki, u'File:' + file_).edit(content % patchTitle, summary=u'Updated %s for [[:%s]].' % (file_, patchTitle), minor=True, bot=True, skipmd5=True)
				success = True
			except Exception, e:
				print e
				n += 1
		if not success:
			print 'Could not upload', file_

if __name__ == '__main__':
	wikiUsername = raw_input('Poot Wiki username: ')
	wikiPassword = getpass.getpass('Poot Wiki password: ')
	patchTitle = raw_input('Poot Wiki patch page title: ')
	gitRepo = raw_input('Poot path of git repo: ')
	print 'Pooting...'
	update_lang_files(wikiUsername, wikiPassword, patchTitle, gitRepo)
	print 'Is gud.'