# -*- coding: utf-8 -*-
# Script to create a pretty diff for TF2 patches and submit them to the wiki
# Written by WindPower

import re
import wikitools

fileRe = re.compile(r'^Index:\s*([^\r\n]*)\s+={10,}[\r\n]+((?:(?!Index:).*[\r\n]+)+)', re.MULTILINE)
lineMatch = re.compile(r'^@@\s*-(\d+),\d+\s*\+(\d+),(\d+)\s*@@$')

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

def pootDiff(wiki, patchName, diffdata):
	diffdata = u(diffdata)
	patchName = u(patchName)
	files = []
	for r in fileRe.finditer(diffdata):
		f = u(r.group(1))
		contents = u(r.group(2)).strip()
		isBinary = contents.find('svn:mime-type = application/octet-stream') != -1
		files.append({
			'name': f,
			'contents': contents,
			'isBinary': isBinary
		})
	def cmpFiles(left, right):
		c1 = cmp(left['isBinary'], right['isBinary'])
		if c1:
			return c1
		return cmp(left['name'], right['name'])
	files.sort(cmp=cmpFiles)
	def formatFile(f):
		isDelete = False
		isAdd = False
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
		for l in lines:
			l = l.replace(u'\r', '').replace(u'\n', '')
			lineRes = lineMatch.search(l)
			if lineRes is not None:
				if not int(lineRes.group(2)) and not int(lineRes.group(3)):
					isDelete = True
					contents = []
					break
				if diffOpen:
					contents.append((u'\u2026'))
				diffOpen = True
				lineOld = int(lineRes.group(1))
				lineNew = int(lineRes.group(2))
			elif (l[:3] == u'---' and l.find(u'(revision 0)') != -1) or l == u'Added: svn:mime-type':
				isAdd = True
			elif l[:14] == u'Cannot display':
				isBinary = True
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
			while n < 5 and not success:
				try:
					wikitools.page.Page(wiki, subPageName).edit(finalText, summary=u'Diff of file "' + f['name'] + u'" for patch [[:' + patchName + u']].', minor=True, bot=True, skipmd5=True)
					success = True
				except:
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

def poot(wikiApi, wikiUsername, wikiPassword, patchName, diffFile):
	wiki = wikitools.wiki.Wiki(wikiApi)
	if wiki.login(wikiUsername, wikiPassword):
		return pootDiff(wiki, patchName, open(diffFile, 'rb').read(-1))
	else:
		print 'Invalid wiki username/password.'

if __name__ == '__main__':
	wikiApi = raw_input('Poot Wiki API URL: ')
	wikiUsername = raw_input('Poot Wiki username: ')
	wikiPassword = raw_input('Poot Wiki password: ')
	patchName = raw_input('Poot Wiki patch page title: ')
	diffFile = raw_input('Poot path of file where diff outpoot is saved: ')
	print 'Pooting...'
	poot(wikiApi, wikiUsername, wikiPassword, patchName, diffFile)
	print 'Is gud.'