# Script to generate a diff for TF2 patches and submit pretty diffs to the wiki
import os, subprocess, re, time, sys, shutil, urllib2, chardet
from subprocess import Popen, PIPE
from prettydiff import poot
from upload_loc_files import update_lang_files
from config import config

TEMP_EXTRACT_DIR = config['tempExtractDir']
GCFS_DIR = config['gcfsDir']

HLEXTRACT_EXE_DIR = config['hlextractExeDir']
VICE_EXE_DIR = config['viceExeDir']

WIKI_USERNAME = config['wikiUsername']
WIKI_PASSWORD = config['wikiPassword']

# Defined variables
## TF2
TEMP_CONTENT_GCF_DIR = TEMP_EXTRACT_DIR + os.sep + r'temp_content'
TEMP_MATERIALS_GCF_DIR = TEMP_EXTRACT_DIR + os.sep + r'temp_materials'
TEMP_CLIENTCONTENT_GCF_DIR = TEMP_EXTRACT_DIR + os.sep + r'temp_client_content'
## TF2 Beta
TEMP_CONTENT_DIR = TEMP_EXTRACT_DIR + os.sep + r'content'
TEMP_CONTENT_DIR2 = TEMP_EXTRACT_DIR + os.sep + r'content2'
TEMP_CONTENT_DIR3 = TEMP_EXTRACT_DIR + os.sep + r'content3'
TEMP_ENGINE_DIR = TEMP_EXTRACT_DIR + os.sep + r'engine'
TEMP_MATERIALS_DIR = TEMP_EXTRACT_DIR + os.sep + r'materials'

WIKI_API = config['wikiApi']

def absPath(path):
	""" Returns correctly formatted absolute directory path. """
	return path if path == r'' else path + os.sep

def compare(sourceDir, targetDir, ignorePattern):
	""" Compares two directories and return list of missing files from the target directory. """
	# extract command line args
	missing = []

	# verify existence of source directory
	if os.path.exists(sourceDir) == False:
		print "sourceDir doesn't exist:", sourceDir
		sys.exit(1)

	if os.path.isdir(sourceDir) == False:
		print "sourceDir not a directory:", sourceDir
		sys.exit(1)

	# verify existence of target directory
	if os.path.exists(targetDir) == False:
		print "targetDir doesn't exist:", targetDir
		sys.exit(1)

	if os.path.isdir(targetDir) == False:
		print "targetDir not a directory:", targetDir
		sys.exit(1)

	# walk the sourceDirectory...
	for root, dirs, files in os.walk(sourceDir):

		subDir = root.replace(sourceDir,'')
		targetSubDir = targetDir + subDir

		regexp = re.compile(ignorePattern, re.IGNORECASE)
		result = regexp.search(targetSubDir)
		if result:
			continue

		# check to see if targetSubDir exists
		if os.path.exists(targetSubDir) == False or os.path.isdir(targetSubDir) == False:
			print "sourceDir {0} not found at {1}".format(root, targetSubDir)
			missing.append(root.replace('\\\\', '\\'))
			continue
		
		# verify that each file in root exists in targetSubDir
		count = 0
		for sourceFile in files:
			# skip symbolic links
			if os.path.islink(root + os.sep + sourceFile):
				continue
			
			targetFile = targetSubDir + os.sep + sourceFile
			if os.path.exists(targetFile) == False:

				# print header if this is the first missing file
				count = count + 1
				if count == 1:
					print "Files in {0} missing from {1}".format(root, targetSubDir)
				missing.append(root.replace('\\\\', '\\') + os.sep + sourceFile)
				print "\t", sourceFile

		# verify that each file in root is indeed a file in targetSubDir
		count = 0
		for sourceFile in files:

			# skip symbolic links
			if os.path.islink(root + os.sep + sourceFile):
				continue
			
			targetFile = targetSubDir + os.sep + sourceFile
			if os.path.exists(targetFile) == True and os.path.isfile(targetFile) == False:

				# print header if this is the first missing file
				count = count + 1
				if count == 1:
					print "Files in {0} not valid files in {1}".format(root, targetSubDir)

				print "\t", sourceFile

		# now diff the source and target files
		count = 0
		for sourceFile in files:

			# skip symbolic links
			if os.path.islink(root + os.sep + sourceFile):
				continue
			
			targetFile = targetSubDir + os.sep + sourceFile
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

try:
	open(absPath(VICE_EXE_DIR) + os.sep + 'vice.exe')
except IOError:
	print 'Could not find vice.exe'
	sys.exit(1)

answer = raw_input('Which game? TF2\\TF2 Beta? ')
if answer.lower() in ['tf2', 'team fortress 2']:
	GAME = 'TF2'
	GIT_DIR = config['tf2GitDir']
	GIT_DIFF_OUTPUT_FILE = config['tf2GitDiffOutputFile']
elif answer.lower() in ['tf2beta', 'tf2 beta', 'team fortress 2 beta', 'tf2b']:
	GAME = 'TF2 Beta'
	GIT_DIR = config['tf2BetaGitDir']
	GIT_DIFF_OUTPUT_FILE = config['tf2BetaGitDiffOutputFile']
else:
	print 'Not off to a good start here...'
	sys.exit(1)

if GAME == 'TF2':
	answer = raw_input('Patch notes available? y\\n? ')
	if answer.lower() in ['yes', 'y', 'yep']:
		patch_notes_exist = True
	elif answer.lower() in ['no', 'n', 'nope']:
		patch_notes_exist = False
	else:
		print 'A simple yes/no would suffice thanks'
		sys.exit(1)

answer = raw_input('Second patch of the day? y\\n? ')
if answer.lower() in ['yes', 'y', 'yep']:
	n_patch = '2'
elif answer.lower() in ['no', 'n', 'nope']:
	n_patch = None
else:
	print 'A simple yes/no would suffice thanks'
	sys.exit(1)

# Get patch date
time_in_US = time.time() - (8 * 60 * 60)
if GAME == 'TF2':
	patch_page_title = time.strftime('%B %d, %Y Patch', time.localtime(time_in_US))
	remove_zero_re = re.compile(r'(\w+) 0(\d), (\d+) Patch')
	res = remove_zero_re.search(patch_page_title)
	if res:
		patch_page_title = r'{0} {1}, {2} Patch'.format(res.group(1), res.group(2), res.group(3))
	if n_patch:
		patch_page_title = patch_page_title.replace('Patch', 'Patch ' + n_patch)
elif GAME == 'TF2 Beta':
	patch_page_title = time.strftime("%B %d, %Y Patch (Beta)", time.localtime(time_in_US))
	remove_zero_re = re.compile(r'(\w+) 0(\d), (\d+) Patch \(Beta\)')
	res = remove_zero_re.search(patch_page_title)
	if res:
		patch_page_title = r'{0} {1}, {2} Patch (Beta)'.format(res.group(1), res.group(2), res.group(3))
	if n_patch:
		patch_page_title = patch_page_title.replace('Patch', 'Patch ' + n_patch)

# Create temp directories
if GAME == 'TF2':
	os.mkdir(TEMP_CONTENT_GCF_DIR)
	os.mkdir(TEMP_MATERIALS_GCF_DIR)
	os.mkdir(TEMP_CLIENTCONTENT_GCF_DIR)
elif GAME == 'TF2 Beta':
	os.mkdir(TEMP_CONTENT_DIR)
	os.mkdir(TEMP_CONTENT_DIR2)
	os.mkdir(TEMP_CONTENT_DIR3)
	os.mkdir(TEMP_ENGINE_DIR)
	os.mkdir(TEMP_MATERIALS_DIR)

# Extract GCFs to respective temp directories
if GAME == 'TF2':
	materials_gcf_extract_cmd = r'"{0}HLExtract.exe" -p "{1}team fortress 2 materials.gcf" -d "{2}" -e root'.format(absPath(HLEXTRACT_EXE_DIR), absPath(GCFS_DIR), TEMP_MATERIALS_GCF_DIR)
	content_gcf_extract_cmd = r'"{0}HLExtract.exe" -p "{1}team fortress 2 content.gcf" -d "{2}" -e root'.format(absPath(HLEXTRACT_EXE_DIR), absPath(GCFS_DIR), TEMP_CONTENT_GCF_DIR)
	clientcontent_gcf_extract_cmd = r'"{0}HLExtract.exe" -p "{1}team fortress 2 client content.gcf" -d "{2}" -e root'.format(absPath(HLEXTRACT_EXE_DIR), absPath(GCFS_DIR), TEMP_CLIENTCONTENT_GCF_DIR)
elif GAME == 'TF2 Beta':
	materials_gcf_extract_cmd = r'"{0}HLExtract.exe" -p "{1}team fortress 2 beta materials.gcf" -d "{2}" -e root'.format(absPath(HLEXTRACT_EXE_DIR), absPath(GCFS_DIR), TEMP_MATERIALS_DIR)
	content_gcf_extract_cmd = r'"{0}HLExtract.exe" -p "{1}team fortress 2 beta content.gcf" -d "{2}" -e root'.format(absPath(HLEXTRACT_EXE_DIR), absPath(GCFS_DIR), TEMP_CONTENT_DIR)
	content2_gcf_extract_cmd = r'"{0}HLExtract.exe" -p "{1}team fortress 2 beta content2.gcf" -d "{2}" -e root'.format(absPath(HLEXTRACT_EXE_DIR), absPath(GCFS_DIR), TEMP_CONTENT_DIR2)
	content3_gcf_extract_cmd = r'"{0}HLExtract.exe" -p "{1}team fortress 2 beta content3.gcf" -d "{2}" -e root'.format(absPath(HLEXTRACT_EXE_DIR), absPath(GCFS_DIR), TEMP_CONTENT_DIR3)
	engine_gcf_extract_cmd = r'"{0}HLExtract.exe" -p "{1}team fortress 2 beta engine.gcf" -d "{2}" -e root'.format(absPath(HLEXTRACT_EXE_DIR), absPath(GCFS_DIR), TEMP_ENGINE_DIR)

if GAME == 'TF2':
	return_code1 = subprocess.call(materials_gcf_extract_cmd)
	return_code2 = subprocess.call(content_gcf_extract_cmd)
	return_code3 = subprocess.call(clientcontent_gcf_extract_cmd)
	if return_code1 != 0 or return_code2 != 0 or return_code3 != 0:
		shutil.rmtree(TEMP_CONTENT_GCF_DIR)
		shutil.rmtree(TEMP_MATERIALS_GCF_DIR)
		shutil.rmtree(TEMP_CLIENTCONTENT_GCF_DIR)
		print 'Error: Shutdown the Steam client first dummkopf'
		sys.exit(1)
elif GAME == 'TF2 Beta':
	return_code1 = subprocess.call(materials_gcf_extract_cmd)
	return_code2 = subprocess.call(content_gcf_extract_cmd)
	return_code3 = subprocess.call(content2_gcf_extract_cmd)
	return_code4 = subprocess.call(content3_gcf_extract_cmd)
	return_code5 = subprocess.call(engine_gcf_extract_cmd)
	if return_code1 != 0 or return_code2 != 0 or return_code3 != 0 or return_code4 != 0 or return_code5 != 0:
		shutil.rmtree(TEMP_CONTENT_DIR)
		shutil.rmtree(TEMP_CONTENT_DIR2)
		shutil.rmtree(TEMP_CONTENT_DIR3)
		shutil.rmtree(TEMP_ENGINE_DIR)
		shutil.rmtree(TEMP_MATERIALS_DIR)
		print 'Error: Shutdown the Steam client first dummkopf'
		sys.exit(1)

def checkForRemovedFiles(gcfname, gcfdir):
	""" Checks for files missing against git copy and
		deletes them from git repo.
	"""
	print '\nNow checking for %s files removed since last revision...' % gcfname[:-4]

	missingfiles = compare(GIT_DIR + os.sep + gcfname, gcfdir + os.sep + 'root', r'\.git')
	if len(missingfiles) != 0:
		print '\nFiles removed from %s' % gcfname
		for file in missingfiles:
			if os.path.isdir(file):
				shutil.rmtree(file)
			else:
				os.remove(file)
	else:
		print '\nNo files removed from %s' % gcfname

if GAME == 'TF2':
	checkForRemovedFiles('team fortress 2 content.gcf', TEMP_CONTENT_GCF_DIR)
	checkForRemovedFiles('team fortress 2 materials.gcf', TEMP_MATERIALS_GCF_DIR)
	checkForRemovedFiles('team fortress 2 client content.gcf', TEMP_CLIENTCONTENT_GCF_DIR)
elif GAME == 'TF2 Beta':
	checkForRemovedFiles('team fortress 2 beta content.gcf', TEMP_CONTENT_DIR)
	checkForRemovedFiles('team fortress 2 beta content2.gcf', TEMP_CONTENT_DIR2)
	checkForRemovedFiles('team fortress 2 beta content3.gcf', TEMP_CONTENT_DIR3)
	checkForRemovedFiles('team fortress 2 beta materials.gcf', TEMP_MATERIALS_DIR)
	checkForRemovedFiles('team fortress 2 beta engine.gcf', TEMP_ENGINE_DIR)

# Convert .txt files to utf-8 and decrypt .ctx files
print '\nConverting relevant files to utf-8 and decrypting ctx files'

def reEncode(fullpath):
	filecontents = open(fullpath, 'rb').read()
	encoding = returnEncoding(filecontents)
	utf8_string = unicode(filecontents, encoding).encode("utf-8")
	open(fullpath, 'wb').write(utf8_string)

def textEncodeDecrypt(dir):
	for root, dirs, files in os.walk(dir):
		for f in files:
			if f[-4:] == r'.txt':
				try:
					fullpath = os.path.join(root, f)
					reEncode(fullpath)
				except:
					pass
			elif f[-4:] == r'.ctx':
				try:
					fullpath = os.path.join(root, f)
					std, err = subprocess.Popen('{0}vice.exe -d -x .ctx -k E2NcUkG2 {1}'.format(absPath(VICE_EXE_DIR), fullpath), stdout=subprocess.PIPE).communicate()
					if err is not None:
						print 'failed to decrypt', fullpath
						sys.exit(1)
					reEncode(fullpath)
				except:
					print 'failed to decrypt', fullpath
					sys.exit(1)

if GAME == 'TF2':
	textEncodeDecrypt(TEMP_CONTENT_GCF_DIR)
elif GAME == 'TF2 Beta':
	textEncodeDecrypt(TEMP_CONTENT_DIR)
	textEncodeDecrypt(TEMP_CONTENT_DIR2)
	textEncodeDecrypt(TEMP_CONTENT_DIR3)

# Merge revisions
print '\nMoving files over'

if GAME == 'TF2':
	moveDirectory(TEMP_CONTENT_GCF_DIR + os.sep + r'root', GIT_DIR + os.sep + r'team fortress 2 content.gcf')
	moveDirectory(TEMP_MATERIALS_GCF_DIR + os.sep + r'root', GIT_DIR + os.sep + r'team fortress 2 materials.gcf')
	moveDirectory(TEMP_CLIENTCONTENT_GCF_DIR + os.sep + r'root', GIT_DIR + os.sep + r'team fortress 2 client content.gcf')
elif GAME == 'TF2 Beta':
	moveDirectory(TEMP_CONTENT_DIR + os.sep + r'root', GIT_DIR + os.sep + r'team fortress 2 beta content.gcf')
	moveDirectory(TEMP_CONTENT_DIR2 + os.sep + r'root', GIT_DIR + os.sep + r'team fortress 2 beta content2.gcf')
	moveDirectory(TEMP_CONTENT_DIR3 + os.sep + r'root', GIT_DIR + os.sep + r'team fortress 2 beta content3.gcf')
	moveDirectory(TEMP_MATERIALS_DIR + os.sep + r'root', GIT_DIR + os.sep + r'team fortress 2 beta materials.gcf')
	moveDirectory(TEMP_ENGINE_DIR + os.sep + r'root', GIT_DIR + os.sep + r'team fortress 2 beta engine.gcf')

# Delete temp directories
print '\nDeleting temp folders'

if GAME == 'TF2':
	shutil.rmtree(TEMP_CONTENT_GCF_DIR)
	shutil.rmtree(TEMP_MATERIALS_GCF_DIR)
	shutil.rmtree(TEMP_CLIENTCONTENT_GCF_DIR)
elif GAME == 'TF2 Beta':
	shutil.rmtree(TEMP_CONTENT_DIR)
	shutil.rmtree(TEMP_CONTENT_DIR2)
	shutil.rmtree(TEMP_CONTENT_DIR3)
	shutil.rmtree(TEMP_MATERIALS_DIR)
	shutil.rmtree(TEMP_ENGINE_DIR)

# Stage all changes to git repo
print '\nStaging changes in git repo'
subprocess.Popen(['git', 'add', '-A'], shell=True, cwd=GIT_DIR).communicate()

# Commit to wiki
print '\nSubmitting prettydiff to wiki'
poot(WIKI_API, WIKI_USERNAME, WIKI_PASSWORD, patch_page_title, GIT_DIR)

# Get git .diff
print '\nGenerating git diff file'
outputfile = open(GIT_DIFF_OUTPUT_FILE, 'wb')
subprocess.Popen(['git', 'diff', '-U', '--cached'], shell=True, stdout=outputfile, cwd=GIT_DIR).communicate()

if GAME == 'TF2':
	# Update localization files
	print '\nUpdating wiki localization files'
	update_lang_files(WIKI_USERNAME, WIKI_PASSWORD, patch_page_title, GIT_DIR)

# Commit to repo
print '\nCommiting to repo'

if GAME == 'TF2':
	if patch_notes_exist:
		commit_message1 = patch_page_title
		commit_message2 = returnPatchNotesURL()
		commit_message3 = r'http://wiki.teamfortress.com/wiki/' + patch_page_title.replace(' ', '_')
		commit_message = ['-m', commit_message1, '-m', commit_message2, '-m', commit_message3]
	else:
		commit_message1 = patch_page_title
		commit_message2 = r'http://wiki.teamfortress.com/wiki/' + patch_page_title.replace(' ', '_')
		commit_message = ['-m', commit_message1, '-m', commit_message2]
elif GAME == 'TF2 Beta':
	commit_message1 = patch_page_title
	commit_message2 = r'http://wiki.teamfortress.com/wiki/' + patch_page_title.replace(' ', '_')
	commit_message = ['-m', commit_message1, '-m', commit_message2]

subprocess.Popen(['git', 'commit'] + commit_message, shell=True, cwd=GIT_DIR).communicate()

# Push up to remote repo
# Do stuff here

print 'All done!'