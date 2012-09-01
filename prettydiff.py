# -*- coding: utf-8 -*-
# Script to create a pretty diff for TF2 patches and submit them to the wiki
# Written by WindPower

import re
import wikitools
import git

lineMatch = re.compile(r'^@@\s*-(\d+),\d+\s*\+(\d+),(\d+)\s*@@')
lineMatch2 = re.compile(r'^@@\s*-(\d+)\s*\+(\d+),(\d+)\s*@@')
lineMatch3 = re.compile(r'^@@\s*-(\d+),\d+\s*\+(\d+)\s*@@')

binaryFileRe = re.compile(r'^Binary files (.+) and (.+) differ')
textFileRe = re.compile(r'^--- (.[^\n]+)\n\+\+\+ (.[^\n]+)\n(.+)', re.DOTALL)

def u(s):
	if type(s) is type(u''):
		return s
	if type(s) is type(''):
		try:
			return unicode(s)
		except:
			try:
				return unicode(s.decode('utf8'))
			except:
				try:
					return unicode(s.decode('windows-1252'))
				except:
					return unicode(s, errors='ignore')
	try:
		return unicode(s)
	except:
		try:
			return u(str(s))
		except:
			return s

def pootDiff(wiki, patchName, gitRepo):
	patchName = u(patchName)
	files = []
	repo = git.Repo(gitRepo)
	head_commit = repo.head.commit
	diffs = head_commit.diff(create_patch = True)

	for diff in diffs:
		if re.search(binaryFileRe, diff.diff) is not None:
			isBinary = True
			contents = u''
		else:
			isBinary = False
			contents = u(re.search(textFileRe, diff.diff).group(3)).strip()

		if diff.a_mode and isBinary:
			f = re.search(binaryFileRe, diff.diff).group(1)[2:].strip()
		elif diff.a_mode and not isBinary:
			f = re.search(textFileRe, diff.diff).group(1)[2:].strip()
		elif diff.b_mode and isBinary:
			f = re.search(binaryFileRe, diff.diff).group(2)[2:].strip()
		elif diff.b_mode and not isBinary:
			f = re.search(textFileRe, diff.diff).group(2)[2:].strip()
		
		isNew = diff.new_file
		isDeleted = diff.deleted_file

		files.append({
			'name': f,
			'contents': contents,
			'isBinary': isBinary,
			'isNew': isNew,
			'isDeleted': isDeleted
		})

	def cmpFiles(left, right):
		c1 = cmp(left['isBinary'], right['isBinary'])
		if c1:
			return c1
		return cmp(left['name'], right['name'])
	files.sort(cmp=cmpFiles)

	def formatFile(f):
		isDelete = f['isDeleted']
		isAdd = f['isNew']
		isBinary = f['isBinary']
		contents = []
		lines = f['contents'].split(u'\n')

		def getLineContent(l):
			if not l.strip():
				return u'&nbsp;'
			return l.replace(u'\t', u'        ')
		diffOpen = False
		lineOld = -1
		lineNew = -1

		if not isBinary:
			for l in lines:
				l = l.replace(u'\r', '').replace(u'\n', '')
				lineRes = lineMatch.search(l)
				lineRes2 = lineMatch2.search(l)
				lineRes3 = lineMatch3.search(l)
				
				if lineRes is not None or lineRes2 is not None or lineRes3 is not None:
					if lineRes:
						res = lineRes.group(1)
						res2 = lineRes.group(2)
						res3 = lineRes.group(3)
					elif lineRes2:
						res = lineRes2.group(1)
						res2 = lineRes2.group(2)
						res3 = lineRes2.group(3)
					elif lineRes3:
						res = lineRes3.group(1)
						res2 = lineRes3.group(2)
						res3 = 1

					if diffOpen:
						contents.append((u'\u2026'))
					diffOpen = True
					lineOld = int(res)
					lineNew = int(res2)
				elif diffOpen and len(l):
					if l[0] == u' ':
						contents.append((u' ', lineOld, lineNew, l[1:]))
						lineOld += 1
						lineNew += 1
					elif l[0] == u'+':
						contents.append((u'+', lineNew, l[1:]))
						lineNew += 1
					elif l[0] == u'-':
						contents.append((u'-', lineOld, l[1:]))
						lineOld += 1
		ret = u'<div class="diff-file'
		if isDelete:
			ret += u' diff-file-deleted'
		ret += u'"><div class="'
		if isBinary:
			ret += u'diff-name-binary'
		else:
			ret += u'diff-name-text'
		ret += u'">'
		if isAdd:
			ret += u'Added'
		elif isDelete:
			ret += u'Deleted'
		else:
			ret += u'Modified'
		ret += u': <span class="diff-name">'
		subPageName = u'Template:PatchDiff/' + patchName + u'/' + f['name']
		if not isBinary:
			ret += u'[[' + subPageName + u'|' + f['name'] + u']]'
		else:
			ret += f['name']
		ret += u'</span></div>'
		if len(contents):
			ret += u'<div class="diff-contents"></div>'
			diffRet = []
			lastBlock = None
			for c in contents:
				if not len(c):
					continue
				d = u'<div class="diff-line-entry'
				if c[0] == u' ':
					d += u' diff-line-nochange'
				elif c[0] == u'+':
					d += u' diff-line-add'
				elif c[0] == u'-':
					d += u' diff-line-remove'
				else: # Ellipsis
					diffRet.append(u'<div class="diff-line-ellipsis">\u2026</div>')
					lastBlock = None
					classIndex = diffRet[-1].find(u'">')
					if classIndex != -1:
						diffRet[-1] = diffRet[-1][:classIndex] + u' diff-line-last' + diffRet[-1][classIndex:]
					continue
				if c[0] != lastBlock:
					d += u' diff-line-first'
					if lastBlock is not None:
						classIndex = diffRet[-1].find(u'">')
						if classIndex != -1:
							diffRet[-1] = diffRet[-1][:classIndex] + u' diff-line-last' + diffRet[-1][classIndex:]
				lastBlock = c[0]
				d += u'">'
				if c[0] == u' ':
					d += u'<span class="diff-line-old">' + u(c[1]) + u'</span><span class="diff-line-new">' + u(c[2]) + u'</span>'
				elif c[0] == u'+':
					d += u'<span class="diff-line-old diff-line-na">N/A</span><span class="diff-line-new">' + u(c[1]) + u'</span>'
				elif c[0] == u'-':
					d += u'<span class="diff-line-old">' + u(c[1]) + u'</span><span class="diff-line-new diff-line-na">N/A</span>'
				d += u'<span class="diff-line">' + getLineContent(c[-1]) + u'</span></div>'
				diffRet.append(d)
			finalText = u(u''.join(diffRet))
			n = 0
			success = False
			while n < 10 and not success:
				try:
					wikitools.page.Page(wiki, subPageName).edit(finalText, summary=u'Diff of file "' + f['name'] + u'" for patch [[:' + patchName + u']].', minor=True, bot=True, skipmd5=True, timeout=60)
					success = True
				except:
					print 'Failed to edit, attempt %s of 10' % str(n)
					n += 1
			if not success:
				wikitools.page.Page(wiki, subPageName).edit(u'<div class="diff-file">File too large to diff</div>', summary=u'Diff of file "' + f['name'] + u'" for patch [[:' + patchName + u']].', minor=True, bot=True, skipmd5=True)
		ret += u'</div>'
		return ret
	patchDiff = u''

	for f in files:
		print 'Processing file:', f['name'], 'in patch:', patchName
		d = formatFile(f)
		patchDiff += d
		print d
	print 'Editing patch diff page:', u'Template:PatchDiff/' + patchName
	wikitools.page.Page(wiki, u'Template:PatchDiff/' + patchName).edit(patchDiff, summary=u'Diff of patch [[:' + patchName + u']].', minor=True, bot=True)

def poot(wikiApi, wikiUsername, wikiPassword, patchName, gitRepo):
	wiki = wikitools.wiki.Wiki(wikiApi)
	if wiki.login(wikiUsername, wikiPassword):
		return pootDiff(wiki, patchName, gitRepo)
	else:
		print 'Invalid wiki username/password.'

if __name__ == '__main__':
	wikiApi = raw_input('Poot Wiki API URL: ')
	wikiUsername = raw_input('Poot Wiki username: ')
	wikiPassword = raw_input('Poot Wiki password: ')
	patchName = raw_input('Poot Wiki patch page title: ')
	gitRepo = raw_input('Poot path of git repo: ')
	print 'Pooting...'
	poot(wikiApi, wikiUsername, wikiPassword, patchName, gitRepo)
	print 'Is gud.'