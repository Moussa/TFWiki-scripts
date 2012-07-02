# A script to upload updated tf_*.txt files after a patch to the wiki

import re, os
import wikitools
from uploadFile import *

fileRe = re.compile(r'^Index:\s*([^\r\n]*)\s+={10,}[\r\n]+((?:(?!Index:).*[\r\n]+)+)', re.MULTILINE)

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

def update_lang_files(wikiUsername, wikiPassword, diffFile, patchTitle, svnDirectory, wikiAddress = r'http://wiki.tf2.com/w/', wikiApi = r'http://wiki.tf2.com/w/api.php'):
	diffdata = open(diffFile, 'rb').read(-1)
	files = []
	for r in fileRe.finditer(diffdata):
		f = os.path.split(r.group(1))[1]
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
				uploader.upload(svnDirectory + os.sep + r'team fortress 2 content.gcf\tf\resource' + os.sep + file, u'File:' + file, u'Uploaded new revision of %s for [[:%s]].' % (file, patchTitle), '', overwrite=True)
				wikitools.page.Page(wiki, u'File:' + file).edit(content % patchTitle, summary=u'Updated %s for [[:%s]].' % (file, patchTitle), minor=True, bot=True, skipmd5=True)
				success = True
			except:
				n += 1
		if not success:
			print 'Could not upload', file

if __name__ == '__main__':
	wikiUsername = raw_input('Poot Wiki username: ')
	wikiPassword = raw_input('Poot Wiki password: ')
	patchTitle = raw_input('Poot Wiki patch page title: ')
	diffFile = raw_input('Poot path of file where diff outpoot is saved: ')
	svnDirectory = raw_input('Poot path of svn directory: ')
	print 'Pooting...'
	update_lang_files(wikiUsername, wikiPassword, diffFile, patchTitle, svnDirectory)
	print 'Is gud.'