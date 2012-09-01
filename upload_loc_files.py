# -*- coding: utf-8 -*-
# A script to upload updated tf_*.txt files after a patch to the wiki

import re, os
import wikitools
import git
from uploadFile import *

binaryFileRe = re.compile(r'^Binary files (.+) and (.+) differ')
textFileRe = re.compile(r'^--- (.[^\n]+)\n\+\+\+ (.[^\n]+)\n(.+)', re.DOTALL)

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

def update_lang_files(wikiUsername, wikiPassword, patchTitle, gitRepo, wikiAddress = r'http://wiki.tf2.com/w/', wikiApi = r'http://wiki.tf2.com/w/api.php'):
	files = []
	repo = git.Repo(gitRepo)
	head_commit = repo.head.commit
	diffs = head_commit.diff(create_patch = True)
	for diff in diffs:
		if re.search(binaryFileRe, diff.diff) is not None:
			isBinary = True
		else:
			isBinary = False

		if diff.a_mode and isBinary:
			f = re.search(binaryFileRe, diff.diff).group(1)[2:].strip()
		elif diff.a_mode and not isBinary:
			f = re.search(textFileRe, diff.diff).group(1)[2:].strip()
		elif diff.b_mode and isBinary:
			f = re.search(binaryFileRe, diff.diff).group(2)[2:].strip()
		elif diff.b_mode and not isBinary:
			f = re.search(textFileRe, diff.diff).group(2)[2:].strip()
		f = os.path.split(f)[1]
		if f.startswith('tf_') and f.endswith('.txt'):
			files.append(f)

	uploader = wikiUpload.wikiUploader(wikiUsername, wikiPassword, wikiAddress)
	wiki = wikitools.wiki.Wiki(wikiApi)
	wiki.login(wikiUsername, wikiPassword)
	for file in files:
		success = False
		n = 0
		while n < 5 and not success:
			try:
				#uploader.upload(gitRepo + os.sep + r'team fortress 2 content.gcf\tf\resource' + os.sep + file, u'File:' + file, u'Uploaded new revision of %s for [[:%s]].' % (file, patchTitle), '', overwrite=True)
				#wikitools.page.Page(wiki, u'File:' + file).edit(content % patchTitle, summary=u'Updated %s for [[:%s]].' % (file, patchTitle), minor=True, bot=True, skipmd5=True)
				print 'uploading:', gitRepo + os.sep + r'team fortress 2 content.gcf\tf\resource' + os.sep + file
				success = True
			except:
				n += 1
		if not success:
			print 'Could not upload', file

if __name__ == '__main__':
	wikiUsername = raw_input('Poot Wiki username: ')
	wikiPassword = raw_input('Poot Wiki password: ')
	patchTitle = raw_input('Poot Wiki patch page title: ')
	gitRepo = raw_input('Poot path of git repo: ')
	print 'Pooting...'
	update_lang_files(wikiUsername, wikiPassword, patchTitle, gitRepo)
	print 'Is gud.'