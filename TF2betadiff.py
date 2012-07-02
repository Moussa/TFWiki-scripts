# Script to generate a diff for TF2 Beta patches and submit pretty diffs to the wiki

import os, subprocess, re, time, sys, shutil, urllib2, chardet
from subprocess import Popen, PIPE
from prettydiff import poot

# Poot user settings here
SVN_DIR = r'' # Directory where SVN local repo exists
TEMP_EXTRACT_DIR = r'' # Directory where files will be temporarily stored. (lots of writing/reading)
GCFS_DIR = r'' # Directory where GCFs reside

HLEXTRACT_EXE_DIR = r'' # Location of HLExtract.exe (http://nemesis.thewavelength.net/index.php?p=35)
VICE_EXE_DIR = r'' # Location of vice.exe for ctx file decryption (http://forums.alliedmods.net/attachment.php?attachmentid=25758&d=1208382645)

SVN_DIFF_OUTPUT_FILE = r'' #Location and name of file for svn diff output
SVN_USERNAME = r'' # SVN repo username
SVN_PASSWORD = r'' # SVN repo password
WIKI_USERNAME = r'' #OTFWiki username
WIKI_PASSWORD = r'' #OTFWiki password

# Defined variables
TEMP_CONTENT_DIR = TEMP_EXTRACT_DIR + os.sep + r'content'
TEMP_CONTENT_DIR2 = TEMP_EXTRACT_DIR + os.sep + r'content2'
TEMP_CONTENT_DIR3 = TEMP_EXTRACT_DIR + os.sep + r'content3'
TEMP_ENGINE_DIR = TEMP_EXTRACT_DIR + os.sep + r'engine'
TEMP_MATERIALS_DIR = TEMP_EXTRACT_DIR + os.sep + r'materials'

WIKI_API = r'http://wiki.tf2.com/w/api.php'

def absPath(path):
	""" Returns correctly formatted absolute directory path. """
	return path if path == r'' else path + os.sep

def compare(sourceDir, targetDir):
	""" Compares two directories and return list of missing files from the target directory. """
	# extract command line args
	missing = []

	# verify existence of source directory
	if os.path.exists(sourceDir) == False:
		print "sourceDir doesn't exist: %s" % sourceDir
		sys.exit(1)

	if os.path.isdir(sourceDir) == False:
		print "sourceDir not a directory: %s" % sourceDir
		sys.exit(1)

	# verify existence of target directory
	if os.path.exists(targetDir) == False:
		print "targetDir doesn't exist: %s" % targetDir
		sys.exit(1)

	if os.path.isdir(targetDir) == False:
		print "targetDir not a directory: %s" % targetDir
		sys.exit(1)

	# walk the sourceDirectory...
	for root, dirs, files in os.walk(sourceDir):

		subDir = root.replace(sourceDir,'')
		targetSubDir = targetDir + subDir
		
		pattern = r'\.svn'
		regexp = re.compile(pattern, re.IGNORECASE)
		result = regexp.search(targetSubDir)
		if result:
				continue

		# check to see if targetSubDir exists
		if os.path.exists(targetSubDir) == False or os.path.isdir(targetSubDir) == False:
			print
			print "sourceDir %s not found at %s" % (root, targetSubDir)
			missing.append(root.replace('\\\\', '\\'))
			continue
		
		# verify that each file in root exists in targetSubDir
		count = 0
		for sourceFile in files:
			# skip symbolic links
			if os.path.islink(root + '/' + sourceFile):
				continue
			
			targetFile = targetSubDir + '/' + sourceFile
			if os.path.exists(targetFile) == False:

				# print header if this is the first missing file
				count = count + 1
				if count == 1:
					print
					print "Files in %s missing from %s" % (root, targetSubDir)
				missing.append(root.replace('\\\\', '\\') + '\\' + sourceFile)
				print "\t%s" % (sourceFile)

		# verify that each file in root is indeed a file in targetSubDir
		count = 0
		for sourceFile in files:

			# skip symbolic links
			if os.path.islink(root + '/' + sourceFile):
				continue
			
			targetFile = targetSubDir + '/' + sourceFile
			if os.path.exists(targetFile) == True and os.path.isfile(targetFile) == False:

				# print header if this is the first missing file
				count = count + 1
				if count == 1:
					print
					print "Files in %s not valid files in %s" % (root, targetSubDir)

				print "\t%s" % (sourceFile)

		# now diff the source and target files
		count = 0
		for sourceFile in files:

			# skip symbolic links
			if os.path.islink(root + '/' + sourceFile):
				continue
			
			targetFile = targetSubDir + '/' + sourceFile
	return missing

def moveDirectory(root_src_dir, root_dst_dir):
	""" Move and overwrite root_dst_dir with contents of root_src_dir. """
	for src_dir, dirs, files in os.walk(root_src_dir):
		dst_dir = src_dir.replace(root_src_dir, root_dst_dir)
		if not os.path.exists(dst_dir):
			os.mkdir(dst_dir)
		for file_ in files:
			src_file = os.path.join(src_dir, file_)
			dst_file = os.path.join(dst_dir, file_)
			if os.path.exists(dst_file):
				os.remove(dst_file)
			shutil.move(src_file, dst_dir)

def returnEncoding(string):
	""" Returns encoding of string. """
	encoding = chardet.detect(string)
	return encoding['encoding']

def svnDelete(filename):
	""" Deletes file from SVN repo. """
	subprocess.call(r'svn delete ' + "\"" + filename + "\"")

# Get patch date. Will be used later
success = False
while not success:
	try:
		timeInUS = time.time() - (8 * 60 * 60)
		patchPageTitle = time.strftime("%B %d, %Y Patch (Beta)", time.localtime(timeInUS))
		removezero = re.compile(r'(\w+) 0(\d), (\d+) Patch \(Beta\)')
		if removezero.search(patchPageTitle):
			patchPageTitle = removezero.search(patchPageTitle).group(1) + ' ' + removezero.search(patchPageTitle).group(2) + ', ' + removezero.search(patchPageTitle).group(3) + ' ' + 'Patch (Beta)'
		success = True
	except:
		continue

answer = raw_input('Second patch of the day? y\\n? ')
if answer in ['yes','y','yep']:
	patchPageTitle += ' 2'
elif answer in ['no','n','nope']:
	pass
else:
	print 'A simple yes/no would suffice thanks'
	sys.exit(1)

# Create temp directories
os.mkdir(TEMP_CONTENT_DIR)
os.mkdir(TEMP_CONTENT_DIR2)
os.mkdir(TEMP_CONTENT_DIR3)
os.mkdir(TEMP_ENGINE_DIR)
os.mkdir(TEMP_MATERIALS_DIR)

# Extract GCFs to respective temp directories
materials_gcf_extract_cmd = r'"%sHLExtract.exe" -p "%steam fortress 2 beta materials.gcf" -d "%s" -e root' % (absPath(HLEXTRACT_EXE_DIR), absPath(GCFS_DIR), TEMP_MATERIALS_DIR)
content_gcf_extract_cmd = r'"%sHLExtract.exe" -p "%steam fortress 2 beta content.gcf" -d "%s" -e root' % (absPath(HLEXTRACT_EXE_DIR), absPath(GCFS_DIR), TEMP_CONTENT_DIR)
content2_gcf_extract_cmd = r'"%sHLExtract.exe" -p "%steam fortress 2 beta content2.gcf" -d "%s" -e root' % (absPath(HLEXTRACT_EXE_DIR), absPath(GCFS_DIR), TEMP_CONTENT_DIR2)
content3_gcf_extract_cmd = r'"%sHLExtract.exe" -p "%steam fortress 2 beta content3.gcf" -d "%s" -e root' % (absPath(HLEXTRACT_EXE_DIR), absPath(GCFS_DIR), TEMP_CONTENT_DIR3)
engine_gcf_extract_cmd = r'"%sHLExtract.exe" -p "%steam fortress 2 beta engine.gcf" -d "%s" -e root' % (absPath(HLEXTRACT_EXE_DIR), absPath(GCFS_DIR), TEMP_ENGINE_DIR)

returnCode1 = subprocess.call(materials_gcf_extract_cmd)
returnCode2 = subprocess.call(content_gcf_extract_cmd)
returnCode3 = subprocess.call(content2_gcf_extract_cmd)
returnCode4 = subprocess.call(content3_gcf_extract_cmd)
returnCode5 = subprocess.call(engine_gcf_extract_cmd)
if returnCode1 != 0 or returnCode2 != 0 or returnCode3 != 0 or returnCode4 != 0 or returnCode5 != 0:
	shutil.rmtree(TEMP_CONTENT_DIR)
	shutil.rmtree(TEMP_CONTENT_DIR2)
	shutil.rmtree(TEMP_CONTENT_DIR3)
	shutil.rmtree(TEMP_ENGINE_DIR)
	shutil.rmtree(TEMP_MATERIALS_DIR)
	print 'Error: Shutdown the Steam client first dummkopf'
	sys.exit(1)

# Check for files missing against SVN copy
print "\nNow checking for files removed since last revision..."

def checkForRemovedFiles(gcfname, gcfdir):
	""" Checks for files missing against SVN copy and
		deletes them from SVN repo.
	"""
	print '\nNow checking for %s files removed since last revision...' % gcfname[:-4]

	missingfiles = compare(SVN_DIR + os.sep + gcfname, gcfdir + os.sep + 'root')
	if len(missingfiles) != 0:
		print '\nFiles removed from %s' % gcfname
		for file in missingfiles:
			svnDelete(file)
	else:
		print '\nNo files removed from %s' % gcfname

checkForRemovedFiles('team fortress 2 beta content.gcf', TEMP_CONTENT_DIR)
checkForRemovedFiles('team fortress 2 beta content2.gcf', TEMP_CONTENT_DIR2)
checkForRemovedFiles('team fortress 2 beta content3.gcf', TEMP_CONTENT_DIR3)
checkForRemovedFiles('team fortress 2 beta materials.gcf', TEMP_MATERIALS_DIR)
checkForRemovedFiles('team fortress 2 beta engine.gcf', TEMP_ENGINE_DIR)

# Convert .txt files to utf-8 and decrypt .ctx files
print "\nConverting relevant files to utf-8 and decrypting ctx files"

def textParse(dir):
	""" Encodes .txt files un 'utf-8' and decrypts .ctx files. """
	for root, dirs, files in os.walk(dir):
		for f in files:
			if f[-4:] == r'.txt':
				try:
					fullpath = os.path.join(root, f)
					filecontents = open(fullpath, 'rb').read()
					encoding = returnEncoding(filecontents)
					utf8string = unicode(filecontents, encoding).encode("utf-8")
					open(fullpath, 'wb').write(utf8string)
				except:
					pass
			elif f[-4:] == r'.ctx':
				try:
					fullpath = os.path.join(root, f)
					returnCode = subprocess.call('%svice.exe -d -x .ctx -k E2NcUkG2 %s' % (absPath(VICE_EXE_DIR), fullpath), stdout=subprocess.PIPE)
					if returnCode != 0:
						print 'failed to decrypt', fullpath
						sys.exit(1)
				except:
					pass

textParse(TEMP_CONTENT_DIR)
textParse(TEMP_CONTENT_DIR2)
textParse(TEMP_CONTENT_DIR3)

# Merge new and SVN versions
print "\nCopying files over"

moveDirectory(TEMP_CONTENT_DIR + os.sep + r'root', SVN_DIR + os.sep + r'team fortress 2 beta content.gcf')
moveDirectory(TEMP_CONTENT_DIR2 + os.sep + r'root', SVN_DIR + os.sep + r'team fortress 2 beta content2.gcf')
moveDirectory(TEMP_CONTENT_DIR3 + os.sep + r'root', SVN_DIR + os.sep + r'team fortress 2 beta content3.gcf')
moveDirectory(TEMP_MATERIALS_DIR + os.sep + r'root', SVN_DIR + os.sep + r'team fortress 2 beta materials.gcf')
moveDirectory(TEMP_ENGINE_DIR + os.sep + r'root', SVN_DIR + os.sep + r'team fortress 2 beta engine.gcf')

# Delete temp directories
print "\nDeleting temp folders"

shutil.rmtree(TEMP_CONTENT_DIR)
shutil.rmtree(TEMP_CONTENT_DIR2)
shutil.rmtree(TEMP_CONTENT_DIR3)
shutil.rmtree(TEMP_MATERIALS_DIR)
shutil.rmtree(TEMP_ENGINE_DIR)

# Commit changes to SVN repo
print "\nCommitting changes to SVN repo"

commit_message = patchPageTitle + '\n' + r'http://wiki.teamfortress.com/wiki/' + patchPageTitle.replace(' ', '_')
subprocess.call(['svn', 'add', SVN_DIR + os.sep + r'team fortress 2 beta content.gcf', '--force'])
subprocess.call(['svn', 'add', SVN_DIR + os.sep + r'team fortress 2 beta content2.gcf', '--force'])
subprocess.call(['svn', 'add', SVN_DIR + os.sep + r'team fortress 2 beta content3.gcf', '--force'])
subprocess.call(['svn', 'add', SVN_DIR + os.sep + r'team fortress 2 beta materials.gcf', '--force'])
subprocess.call(['svn', 'add', SVN_DIR + os.sep + r'team fortress 2 beta engine.gcf', '--force'])
subprocess.call(['svn', 'commit', SVN_DIR + os.sep, '-m', commit_message, '--username', SVN_USERNAME, '--password', SVN_PASSWORD])

# Get SVN diff
print "\nDownloading SVN diff output"

lastRevisionRE = re.compile(r'Revision: (\d+)')
p = Popen('svn info http://tf2svn.biringa.com/betasvn', stdout=PIPE, stderr=PIPE)
stdout, stderr = p.communicate()
result = lastRevisionRE.search(stdout)
lastRevision = int(result.group(1))

q = Popen('svn diff http://tf2svn.biringa.com/betasvn@' + str(lastRevision-1) + ' http://tf2svn.biringa.com/betasvn@' + str(lastRevision), stdout=PIPE, stderr=PIPE)
stdout, stderr = q.communicate()
open(SVN_DIFF_OUTPUT_FILE, "wb").write(stdout)

#Commit to wiki
print "\nSubmitting prettydiff to wiki"
poot(WIKI_API, WIKI_USERNAME, WIKI_PASSWORD, patchPageTitle, SVN_DIFF_OUTPUT_FILE)

print "All done!"