# Script to generate a diff for TF2 patches and submit pretty diffs to the wiki

import os, subprocess, re, time, sys, shutil, urllib2, chardet
from subprocess import Popen, PIPE
from prettydiff import poot
from upload_loc_files import update_lang_files

# Poot user settings here
SVN_DIR = r'' # Directory where SVN local repo exists
TEMP_EXTRACT_DIR = r'' # Directory where files will be temporarily stored. (lots of writing/reading)
GCFS_DIR = r'' # Directory where GCFs reside

HLEXTRACT_EXE_DIR = r'' # Location of HLExtract.exe (http://nemesis.thewavelength.net/index.php?p=35)
PLINK_EXE_DIR = r'' # Location of Plink.exe (http://www.chiark.greenend.org.uk/~sgtatham/putty/download.html)
PSCP_EXE_DIR = r'' # Location of PSCP.exe (http://www.chiark.greenend.org.uk/~sgtatham/putty/download.html)
VICE_EXE_DIR = r'' # Location of vice.exe for ctx file decryption (http://forums.alliedmods.net/attachment.php?attachmentid=25758&d=1208382645)
SSH_PRIVATE_KEY_FILE = r'' # Location of private SSH key file for tf2wiki@biringa.com
SSH_PASS_PHRASE = r'' # Pass phrase for SSH key

SVN_DIFF_OUTPUT_FILE = r'' # Location and name of file for svn diff output
SVN_USERNAME = r'' # SVN repo username
SVN_PASSWORD = r'' # SVN repo password
WIKI_USERNAME = r'' # OTFWiki username
WIKI_PASSWORD = r'' # OTFWiki password

# Defined variables
TEMP_CONTENT_GCF_DIR = TEMP_EXTRACT_DIR + os.sep + r'temp_content'
TEMP_MATERIALS_GCF_DIR = TEMP_EXTRACT_DIR + os.sep + r'temp_materials'
TEMP_CLIENTCONTENT_GCF_DIR = TEMP_EXTRACT_DIR + os.sep + r'temp_client_content'

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

def returnPatchNotesURL():
	""" Returns Steam patch notes URL using Steam feed. """
	feed_URL = 'http://store.steampowered.com/news/posts/?feed=steam_updates&appids=440'
	steam_news_re = re.compile(r'<div[^<>]*class="headline"[^<>]*>(?:(?!class="headline").)*"posttitle"(?:(?!class="headline").)*<a[^<>]*href="http://store\.steampowered\.com/news/(\d+)[^<>]*?>\s*([^<>]*)\s*</a>(?:(?!class="headline").)*<div[^<>]*class="body"[^<>]*>\s*((?:(?!</div>).)*?)\s*</div>', re.IGNORECASE | re.DOTALL)
	steam_news_content = urllib2.urlopen(feed_URL).read(-1)
	res = steam_news_re.search(steam_news_content)
	story_id = res.group(1)
	return 'http://store.steampowered.com/news/' + story_id

def returnEncoding(string):
	""" Returns encoding of string. """
	encoding = chardet.detect(string)
	return encoding['encoding']

def svnDelete(filename):
	""" Deletes file from SVN repo. """
	subprocess.call(r'svn delete ' + "\"" + filename + "\"")

try:
	open('vice.exe')
except IOError:
	print 'Could not find vice.exe'
	sys.exit(1)

# Get patch date. Will be used later
success = False
while not success:
	try:
		time_in_US = time.time() - (8 * 60 * 60)
		patch_page_title = time.strftime('%B %d, %Y Patch', time.localtime(time_in_US))
		remove_zero_re = re.compile(r'(\w+) 0(\d), (\d+) Patch')
		res = remove_zero_re.search(patch_page_title)
		if res:
			patch_page_title = r'%s %s, %s Patch' % (res.group(1), res.group(2), res.group(3))
		success = True
	except:
		continue

answer = raw_input('Patch notes available? y\\n? ')
if answer in ['yes', 'y', 'yep']:
	patch_notes_exist = True
elif answer in ['no', 'n', 'nope']:
	patch_notes_exist = False
else:
	print 'A simple yes/no would suffice thanks'
	sys.exit(1)

answer = raw_input('Second patch of the day? y\\n? ')
if answer in ['yes', 'y', 'yep']:
	patch_page_title += ' 2'
elif answer in ['no', 'n', 'nope']:
	pass
else:
	print 'A simple yes/no would suffice thanks'
	sys.exit(1)

# Create temp directories
os.mkdir(TEMP_CONTENT_GCF_DIR)
os.mkdir(TEMP_MATERIALS_GCF_DIR)
os.mkdir(TEMP_CLIENTCONTENT_GCF_DIR)

# Extract GCFs to respective temp directories
materials_gcf_extract_cmd = r'"%sHLExtract.exe" -p "%steam fortress 2 materials.gcf" -d "%s" -e root' % (absPath(HLEXTRACT_EXE_DIR), absPath(GCFS_DIR), TEMP_MATERIALS_GCF_DIR)
content_gcf_extract_cmd = r'"%sHLExtract.exe" -p "%steam fortress 2 content.gcf" -d "%s" -e root' % (absPath(HLEXTRACT_EXE_DIR), absPath(GCFS_DIR), TEMP_CONTENT_GCF_DIR)
clientcontent_gcf_extract_cmd = r'"%sHLExtract.exe" -p "%steam fortress 2 client content.gcf" -d "%s" -e root' % (absPath(HLEXTRACT_EXE_DIR), absPath(GCFS_DIR), TEMP_CLIENTCONTENT_GCF_DIR)

return_code1 = subprocess.call(materials_gcf_extract_cmd)
return_code2 = subprocess.call(content_gcf_extract_cmd)
return_code3 = subprocess.call(clientcontent_gcf_extract_cmd)
if return_code1 != 0 or return_code2 != 0 or return_code3 != 0:
	shutil.rmtree(TEMP_CONTENT_GCF_DIR)
	shutil.rmtree(TEMP_MATERIALS_GCF_DIR)
	shutil.rmtree(TEMP_CLIENTCONTENT_GCF_DIR)
	print 'Error: Shutdown the Steam client first dummkopf'
	sys.exit(1)

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

checkForRemovedFiles('team fortress 2 content.gcf', TEMP_CONTENT_GCF_DIR)
checkForRemovedFiles('team fortress 2 materials.gcf', TEMP_MATERIALS_GCF_DIR)
checkForRemovedFiles('team fortress 2 client content.gcf', TEMP_CLIENTCONTENT_GCF_DIR)

# Convert .txt files to utf-8 and decrypt .ctx files
print '\nConverting relevant files to utf-8 and decrypting ctx files'

for root, dirs, files in os.walk(TEMP_CONTENT_GCF_DIR):
	for f in files:
		if f[-4:] == r'.txt':
			try:
				fullpath = os.path.join(root, f)
				filecontents = open(fullpath, 'rb').read()
				encoding = returnEncoding(filecontents)
				utf8_string = unicode(filecontents, encoding).encode("utf-8")
				open(fullpath, 'wb').write(utf8_string)
			except:
				pass
		elif f[-4:] == r'.ctx':
			try:
				fullpath = os.path.join(root, f)
				return_code = subprocess.call('%svice.exe -d -x .ctx -k E2NcUkG2 %s' % (absPath(VICE_EXE_DIR), fullpath), stdout=subprocess.PIPE)
				if return_code != 0:
					print 'failed to decrypt', fullpath
					sys.exit(1)
			except:
				print 'failed to decrypt', fullpath
				sys.exit(1)

# Merge revisions
print '\nMoving files over'

moveDirectory(TEMP_CONTENT_GCF_DIR + os.sep + r'root', SVN_DIR + os.sep + r'team fortress 2 content.gcf')
moveDirectory(TEMP_MATERIALS_GCF_DIR + os.sep + r'root', SVN_DIR + os.sep + r'team fortress 2 materials.gcf')
moveDirectory(TEMP_CLIENTCONTENT_GCF_DIR + os.sep + r'root', SVN_DIR + os.sep + r'team fortress 2 client content.gcf')

# Delete temp directories
print '\nDeleting temp folders'

shutil.rmtree(TEMP_CONTENT_GCF_DIR)
shutil.rmtree(TEMP_MATERIALS_GCF_DIR)
shutil.rmtree(TEMP_CLIENTCONTENT_GCF_DIR)

# Commit changes to SVN repo
print '\nCommitting changes to SVN repo'

if patch_notes_exist:
	commit_message = patch_page_title + '\n' + returnPatchNotesURL() + '\n' + r'http://wiki.teamfortress.com/wiki/' + patch_page_title.replace(' ', '_')
else:
	commit_message = patch_page_title + '\n' + r'http://wiki.teamfortress.com/wiki/' + patch_page_title.replace(' ', '_')
subprocess.call(['svn', 'add', SVN_DIR + os.sep + r'team fortress 2 content.gcf', '--force'])
subprocess.call(['svn', 'add', SVN_DIR + os.sep + r'team fortress 2 materials.gcf', '--force'])
subprocess.call(['svn', 'add', SVN_DIR + os.sep + r'team fortress 2 client content.gcf', '--force'])
subprocess.call(['svn', 'commit', SVN_DIR + os.sep, '-m', commit_message, '--username', SVN_USERNAME, '--password', SVN_PASSWORD])

# Get SVN .diff
print '\nGenerating SVN diff file'

last_revision_re = re.compile(r'Revision: (\d+)')
p = Popen('svn info http://tf2svn.biringa.com/svn', stdout=PIPE, stderr=PIPE)
stdout, stderr = p.communicate()
result = last_revision_re.search(stdout)
last_revision = int(result.group(1))

return_code = subprocess.call('"%splink" "tf2wiki@biringa.com" -i "%s" -pw "%s" -batch "cd /home/tf2wiki/tf2co;svn up;svn diff -r %s:%s > \'%s.diff\'"' % (absPath(PLINK_EXE_DIR), SSH_PRIVATE_KEY_FILE, SSH_PASS_PHRASE, str(last_revision-1), str(last_revision), patch_page_title.replace(' ','_')))
if return_code != 0:
	print 'Need more gun son'
	sys.exit(1)
return_code = subprocess.call('"%spscp" -i "%s" -pw "%s" -batch "tf2wiki@biringa.com:/home/tf2wiki/tf2co/%s.diff" "%s"' % (absPath(PSCP_EXE_DIR), SSH_PRIVATE_KEY_FILE, SSH_PASS_PHRASE, patch_page_title.replace(' ','_'), SVN_DIFF_OUTPUT_FILE))
if return_code != 0:
	print 'Need more gun sawbones'
	sys.exit(1)
return_code = subprocess.call('"%splink" "tf2wiki@biringa.com" -i "%s" -pw "%s" -batch "rm /home/tf2wiki/tf2co/%s.diff"' % (absPath(PLINK_EXE_DIR), SSH_PRIVATE_KEY_FILE, SSH_PASS_PHRASE, patch_page_title.replace(' ','_')))
if return_code != 0:
	print 'Need more gun chucklenuts'
	sys.exit(1)

#Commit to wiki
print '\nSubmitting prettydiff to wiki'
poot(WIKI_API, WIKI_USERNAME, WIKI_PASSWORD, patch_page_title, SVN_DIFF_OUTPUT_FILE)

#Update localization files
print '\nUpdating wiki localization files'
update_lang_files(WIKI_USERNAME, WIKI_PASSWORD, SVN_DIFF_OUTPUT_FILE, patch_page_title, SVN_DIR)

print 'All done!'