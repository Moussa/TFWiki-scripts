statusRe = re.compile(r'^(\w)\s+\"?(.[^\"]+)\"?')
statusReRenamed = re.compile(r'^R\s+\"?(.[^\"]+)\"?\s+->\s+\"?(.[^\"]+)\"?')
			filename = newname
				if 'new file mode 100644' not in diff:
					contents = u(re.search(textFileRe, diff).group(3).encode('utf-8')).strip()
				else:
					contents = u''
		subPageName = u'Template:PatchDiff/' + patchName + u'/' + f['name'].replace("{", "(")
			# f = open('difftextout.txt', 'wb')
			# f.write(patchDiff)
			# f.close()