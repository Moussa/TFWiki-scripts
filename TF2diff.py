import os
import subprocess
import re
import time
import sys
import shutil
import chardet
import fnmatch
from ircutils import bot, format
from prettydiff import poot
from upload_loc_files import update_lang_files

from config import config

class AnnounceBot(bot.SimpleBot):
    def __init__(self, nickname, patch, address):
        bot.SimpleBot.__init__(self, nickname)
        self.patch = patch
        self.address = address

    def on_join(self, event):
        message = '{0}: {1} [{2}]'.format(format.color(format.bold('Uploaded patch diff'), format.GREEN),
                                            format.color(format.bold(self.patch), format.DARK_GRAY),
                                            self.address + self.patch.replace(' ', '_') + '#Files_changed'
                                            )
        self.send_message(event.target, message)
        self.quit()

def compare(sourceDir, targetDir, ignorePattern):
    """ Compare two directories and return list of missing files from the target directory """
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

        subDir = root.replace(sourceDir, '')
        targetSubDir = targetDir + subDir

        regexp = re.compile(ignorePattern, re.IGNORECASE)
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
    encoding = chardet.detect(string)
    return encoding['encoding']


def getPatchName(format):
    choices = []
    choice_modifiers = [0, -24, -48, -72]

    for mod in choice_modifiers:
        suggestion = time.strftime(format, time.localtime(time.time() + (mod * 60 * 60))).replace(' 0', ' ') # gets rid of leading zeros on days
        choices.append(suggestion)
    choices.append("Custom")
    choice = get_choice(choices)
    if choice == "Custom":
        name = str(raw_input("Manually enter the correct page name: "))
    else:
        name = choice

    if str(raw_input("Please confirm patch page name: {}  y\\n ".format(name))) != "y":
        suck()

    if str(raw_input("Is this the first patch of the day? y\\n ")) == "n":
        name = name + " {n}".format(n=str(raw_input("If this is the nth patch of the day, what is n?")))

    return name

def reEncode(fullpath):
    filecontents = open(fullpath, 'rb').read()
    encoding = returnEncoding(filecontents)
    utf8_string = unicode(filecontents, encoding).encode("utf-8")
    open(fullpath, 'wb').write(utf8_string)

def txtToUtf8(dir):
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
                    std, err = subprocess.Popen('{0}vice.exe -d -x .ctx -k E2NcUkG2 {1}'.format(r'F:/Mohammed/Desktop/', fullpath), stdout=subprocess.PIPE).communicate()
                    if err is not None:
                        print 'failed to decrypt', fullpath
                        sys.exit(1)
                    reEncode(fullpath)
                except:
                    print 'failed to decrypt', fullpath
                    sys.exit(1)

def suck():
    raw_input("You suck")
    sys.exit()

def get_choice(choices):
    index = 1
    for item in choices:
        print "\t{}: {}".format(index, item)
        index += 1

    choice_input = raw_input("Input the number of your choice: ")
    if choice_input.isdigit():
        choice_input = int(choice_input)
        if choice_input <= 0 or choice_input > len(choices):
            suck()
        else:
            choice = choices[choice_input-1]
    else:
        suck()
    return choice

def main():
    choice = None

    # Check to see which game has been specified via the launch arguments.
    if len(sys.argv) < 2:
        print "Please specify the game to diff"
        choices = []
        for game in config:
            if game != "fallback":
                choices.append(game)
        choice = get_choice(choices)

    # Try load config for specified game.
    try:
        fallback = config["fallback"]
        if choice != None:
            working = config[choice]
        else:
            working = config[sys.argv[1]]

        workingRepoDir = working.get("workingRepoDir", fallback["workingRepoDir"])
        tempDir = working.get("tempDir", fallback["tempDir"])
        gameFolder = working.get("gameFolder", fallback["gameFolder"])
        diffOutput = working.get("diffOutput", fallback["diffOutput"])
        patchNameFormat = working.get("patchNameFormat", fallback["patchNameFormat"])
        wikiApi = working.get("wikiApi", fallback["wikiApi"])
        wikiUsername = working.get("wikiUsername", fallback["wikiUsername"])
        wikiPassword = working.get("wikiPassword", fallback["wikiPassword"])
        wikiArticleAddress = working.get("wikiArticleAddress", None)
        ircChannel = working.get("ircChannel", None)
        hlExtract = working.get("hlExtract", fallback["hlExtract"])
        name = os.path.split(gameFolder)[1]

    except:
        print 'Error: First argument must be a supported game:'
        print supported_games()
        sys.exit(1)

    # Get patch title - get all user input before doing work.
    patchTitle = getPatchName(patchNameFormat)

    auto_wiki = raw_input("Submit diff to wiki upon completion?").lower() != "n"
    start_time = time.mktime(time.gmtime())

    # Create temp directory
    if os.path.isdir(tempDir) != True:
        os.mkdir(tempDir)
    else:
        print "Johnny: \tCAPTAIN, WE HAVE REMNANTS OF AN OLD TEMPDIR!"
        print "Captain: \tARRR, THAT AINT IDEAL.  KABLEWM THE SCALLYWAGS OUTA THE OCEAN I SAY!"
        print "Johnny: \tMENTLEMENS, LASER THE BEEMZ!"
        shutil.rmtree(tempDir)
        print "Sniper: \t Thanks for standin still, ganker!"
        os.mkdir(tempDir)

    # Copy files to temp dir.
    print "Copying files to temp directory"
    copyToTempdir = r'xcopy "{source!s}" "{destination!s}" /E /Q'.format(source = gameFolder, destination = tempDir)
    returnCopyToTempdir = subprocess.call(copyToTempdir, shell=True)
    if returnCopyToTempdir != 0:
        shutil.rmtree(tempDir)
        print 'Error: Shutdown the Steam client first dummkopf'
        sys.exit(1)

    # Extract VPKs
    vpks = []
    for root, dirs, files in os.walk(tempDir):
        for f in files:
            if fnmatch.fnmatch(f, "*.vpk"):
                vpks.append(root + os.sep + f)

    vpk_dirs = []
    for root, dirs, files in os.walk(tempDir):
        for f in files:
            if fnmatch.fnmatch(f, "*_dir.vpk"):
                vpk_dirs.append(root + os.sep + f)

    for vpk in vpk_dirs:
        print "Extracting vpk: {}".format(vpk)

        command = "{hle} -s -p {vpk} -d {dest} -e root".format(hle = hlExtract, vpk = vpk, dest = tempDir)
        return_code = subprocess.call(command)
        assert return_code == 0

        os.remove(vpk)
        shutil.copytree(tempDir + os.sep + "root", vpk)
        shutil.rmtree(tempDir + os.sep + "root")

    for vpk in vpks:
        if os.path.isfile(vpk):
            os.remove(vpk)

    # Find deleted files, remove them from svn
    missingfiles = compare(workingRepoDir, tempDir,  r'\.git')
    if len(missingfiles) != 0:
        print "\nFiles removed from files:"
        for f in missingfiles:
                if os.path.isdir(f):
                    shutil.rmtree(f)
                elif os.path.isfile(f):
                    os.remove(f)
    else:
        print "\nNo files removed from files."

    # Convert .txt files to utf-8
    print "\nConverting relevant files to utf-8 and decrypting ctx files"
    txtToUtf8(tempDir)

    # Moving files to working repository.
    print "\nMoving files to working repository"
    moveDirectory(tempDir, workingRepoDir)

    # Delete temp directories
    print "\nDeleting temporary directory."
    shutil.rmtree(tempDir)

    commit_message = patchTitle
    # Stage all changes to git repo
    print '\nStaging changes in git repo'
    subprocess.Popen(['git', 'add', '-A'], shell=True, cwd=workingRepoDir).communicate()
    
    # Commit to wiki
    if not auto_wiki:
        raw_input("Ready to submit to Wiki.  Hit enter to go ahead.")
    print "\nSubmitting prettydiff to wiki"
    poot(wikiApi, wikiUsername, wikiPassword, patchTitle, workingRepoDir)

    # Announce in IRC
    if ircChannel:
        print "\nAnnouncing completion to IRC channel"
        announcebot = AnnounceBot(wikiUsername, patchTitle, wikiArticleAddress)
        announcebot.connect(r'chat.freenode.net', channel=ircChannel)
        announcebot.start()

    # Get git .diff
    print '\nGenerating git diff file'
    outputfile = open(diffOutput, 'wb')
    subprocess.Popen(['git', 'diff', '-U', '--cached'], shell=True, stdout=outputfile, cwd=workingRepoDir).communicate()

    if game.lower() == 'tf2':
        # Update localization files
        print '\nUpdating wiki localization files'
        update_lang_files(wikiUsername, wikiPassword, patchTitle, workingRepoDir)

    # Commit to repo
    print '\nCommiting to repo'

    commit_message1 = patchTitle
    commit_message = ['-m', commit_message1]

    subprocess.Popen(['git', 'commit'] + commit_message, shell=True, cwd=workingRepoDir).communicate()
    print "Finished. Time taken: {} seconds".format(time.mktime(time.gmtime()) - start_time)
if __name__ == "__main__":
    main()