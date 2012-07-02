# Generates the equip regions table found at
# Template:Equip region table on the wiki

from vdfparser import VDF

schema = VDF()
allitems = schema.get_items()
regionsDict = {}

def add_region(itemname, region):
	global regionsDict
	if region in regionsDict:
		regionsDict[region].append(itemname)
	else:
		regionsDict[region] = []
		regionsDict[region].append(itemname)

for item in allitems:
	item = allitems[item]
	if 'item_name' in item:
		print 'Processing', item['name']
		itemname = schema.get_localized_item_name(item['item_name'])
		if 'equip_region' in item:
			region = item['equip_region']
			if item['equip_region'] != 'hat':
				add_region(itemname, region)
		elif 'equip_regions' in item:
			regions = item['equip_regions']
			for region in regions:
				if region != 'hat':
					add_region(itemname, region)
		if 'prefab' in item and item['prefab'] == 'award_medal':
			region = 'medal'
			add_region(itemname, region)

### Some output fixes here ###
# Replace medals
medalsException = ['First Place - ETF2L Highlander Tournament',
				   'First Place - Gamers With Jobs Tournament',
				   'Participant - ETF2L Highlander Tournament',
				   'Participant - Gamers With Jobs Tournament',
				   'Second Place - ETF2L Highlander Tournament',
				   'Second Place - Gamers With Jobs Tournament',
				   'Third Place - ETF2L Highlander Tournament',
				   'UGC Highlander Iron 1st Place',
				   'UGC Highlander Iron 2nd Place',
				   'UGC Highlander Iron 3rd Place',
				   'UGC Highlander Participant',
				   'UGC Highlander Platinum 1st Place',
				   'UGC Highlander Platinum 2nd Place',
				   'UGC Highlander Platinum 3rd Place',
				   'UGC Highlander Silver 1st Place',
				   'UGC Highlander Silver 2nd Place',
				   'UGC Highlander Silver 3rd Place',
				   'UGC Highlander Euro Iron',
				   'UGC Highlander Euro Participant',
				   'UGC Highlander Euro Platinum',
				   'UGC Highlander Euro Silver',
				   'UGC Highlander Platinum Participant',
				   'UGC Highlander Silver Participant',
				   'UGC Highlander Tin 1st Place',
				   'UGC Highlander Tin 2nd Place',
				   'UGC Highlander Tin 3rd Place',
				   'UGC Highlander 1st Place European Platinum',
                   'UGC Highlander 1st Place European Silver',
				   'UGC Highlander 1st Place European Steel',
				   'UGC Highlander 1st Place North American Platinum',
				   'UGC Highlander 1st Place North American Silver',
				   'UGC Highlander 1st Place North American Steel',
				   'UGC Highlander 1st Place South American Platinum',
				   'UGC Highlander 1st Place South American Steel',
				   'UGC Highlander 2nd Place European Platinum',
				   'UGC Highlander 2nd Place European Silver',
				   'UGC Highlander 2nd Place European Steel',
				   'UGC Highlander 2nd Place North American Platinum',
				   'UGC Highlander 2nd Place North American Silver',
				   'UGC Highlander 2nd Place North American Steel',
				   'UGC Highlander 2nd Place South American Platinum',
				   'UGC Highlander 2nd Place South American Steel',
				   'UGC Highlander 3rd Place European Platinum',
				   'UGC Highlander 3rd Place European Silver',
				   'UGC Highlander 3rd Place European Steel',
				   'UGC Highlander 3rd Place North American Platinum',
				   'UGC Highlander 3rd Place North American Silver',
				   'UGC Highlander 3rd Place North American Steel',
				   'UGC Highlander 3rd Place South American Platinum',
				   'UGC Highlander 3rd Place South American Steel',
				   'UGC Highlander Steel Participant']

regionsDict['medal'] = [item for item in regionsDict['medal'] if not item in medalsException]
regionsDict['medal'].append('Tournament Medal - ETF2L Highlander Tournament')
regionsDict['medal'].append('Tournament Medal - GWJ Tournament')
regionsDict['medal'].append('Tournament Medal - UGC Highlander Tournament')

# Fix Essential Accessories
for region in regionsDict:
	try:
		regionsDict[region].remove('The Essential Accessories')
		regionsDict[region].append('Essential Accessories')
	except:
		pass

regionsDict = sorted(regionsDict.items())
output = """"""

for region in regionsDict:
	regionname = region[0]
	regionitems = region[1]
	regionitems.sort(key=lambda s: (s.lower(), s))
	output += """\n! {{item name|er """ + regionname + """}}"""
	n = 1
	for item in regionitems:
		if len(regionitems) == 1:
			if item == 'Halloween Masks':
				output += """\n| style="font-weight:bold; font-size:0.95em;" | [[File:Heavy Mask.png|40px]] [[Halloween Masks{{if lang}}|{{item name|Halloween Masks}}]]"""
			else:
				output += """\n| style="font-weight:bold; font-size:0.95em;" | {{item nav link|""" + item + """}}"""
		elif n == 1:
			if item == 'Halloween Masks':
				output += """\n| style="font-weight:bold; font-size:0.95em;" | [[File:Heavy Mask.png|40px]] [[Halloween Masks{{if lang}}|{{item name|Halloween Masks}}]]<!--"""
			else:
				output += """\n| style="font-weight:bold; font-size:0.95em;" | {{item nav link|""" + item + """}}<!--"""
			n += 1
		elif n == len(regionitems):
			if item == 'Halloween Masks':
				output += """\n --><br />[[File:Heavy Mask.png|40px]] [[Halloween Masks{{if lang}}|{{item name|Halloween Masks}}]]"""
			else:
				output += """\n --><br />{{item nav link|""" + item + """}}"""
		else:
			if item == 'Halloween Masks':
				output += """\n --><br />[[File:Heavy Mask.png|40px]] [[Halloween Masks{{if lang}}|{{item name|Halloween Masks}}]]<!--"""
			else:
				output += """\n --><br />{{item nav link|""" + item + """}}<!--"""
			n += 1
	output += """\n|-"""
output += """\n|}"""

# Save to file
h = open('equipregions.txt', 'wb')
h.write(output.encode('utf8'))
h.close()
print '\nDone, printed to equipregions.txt' 