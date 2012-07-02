import Image, re, os, subprocess, sys
from vdfparser import VDF
from subprocess import PIPE, Popen
import wikitools
from uploadFile import *

if not os.path.isfile('pngcrush.exe'):
	print 'Could not find pngcrush.exe\nExiting'
	sys.exit()

def get_file_list(folder):
	""" Returns list of .png files in folder. """
	filelist = []
	for file in os.listdir(folder):
		if file.endswith('.png'):
			filelist.append(file)
	return filelist

def crop_image(inputimage, folder, newimgname, xtop=0, ytop=64, xbottom=512, ybottom=448):
	""" Crops input image and writes to newimgname. """
	img = Image.open(folder + os.sep + inputimage)
	img = img.crop((xtop, ytop, xbottom, ybottom))
	img.save(folder + os.sep + newimgname, 'PNG')

def get_item_from_inventory(allitems, imgname):
	""" Returns item with matching image_inventory image name. """
	for item in allitems:
		if 'image_inventory' in allitems[item]:
			if os.path.split(allitems[item]['image_inventory'])[1] == imgname:
				return allitems[item]
	return None

def upload_item_icons(wikiUsername, wikiPassword, folder, wikiAddress = r'http://wiki.tf2.com/w/', wikiApi = r'http://wiki.tf2.com/w/api.php'):
	""" Crops and uploads item icons to wiki. """
	uploader = wikiUpload.wikiUploader(wikiUsername, wikiPassword, wikiAddress)
	wiki = wikitools.wiki.Wiki(wikiApi)
	wiki.login(wikiUsername, wikiPassword)
	schema = VDF()
	fails = False
	allitems = schema.get_items()
	for file in get_file_list(folder):
		imgname = re.sub(r'_large\.png', '', file)
		print imgname
		item = get_item_from_inventory(allitems, imgname)
		if item is None:
			f = open('faileditemiconuploads.txt', 'ab').write(file + '\n')
			fails = True
			continue
		itemname = schema.get_localized_item_name(item['item_name']).encode('utf8')
		newfilename = r'Item icon {0}.png'.format(itemname)
		crop_image(file, folder, newfilename)
		process = Popen(['pngcrush', '-rem', 'gAMA', '-rem', 'cHRM', '-rem', 'iCCP', '-rem', 'sRGB', '-brute', folder + os.sep + newfilename, folder + os.sep + newfilename + 'temp'], stdout = subprocess.PIPE).communicate()[0]
		os.remove(folder + os.sep + newfilename)
		os.rename(folder + os.sep + newfilename + 'temp', folder + os.sep + newfilename)

		success = False
		n = 0
		while n < 5 and not success:
			try:
				uploader.upload(folder + os.sep + newfilename, 'File:' + newfilename, 'Uploaded new TF2B icon', '', overwrite=True)
				success = True
			except:
				n += 1
		if not success:
			print 'Could not upload', newfilename
	if fails:
		print 'Some files could not be uploaded. Please see faileditemiconuploads.txt'

upload_item_icons('wiki_username', 'wiki_password', r'image_folder_path')