# -*- coding: utf-8 -*-
# Generates the equip regions table found at
# http://wiki.tf/Template:Equip_region_table on the wiki

from vdfparser import VDF

schema = VDF()
items = schema.get_items()
prefabs = schema.get_prefabs()
allitems =  dict(items, **prefabs)
regionsDict = {}

def add_region(itemname, region):
    if region in regionsDict:
        if itemname not in regionsDict[region]:
            regionsDict[region].append(itemname)
    else:
        regionsDict[region] = [itemname]
        print 'Added region', region

for item in allitems:
    item = allitems[item]
    if 'item_name' in item:
        print 'Processing', item['item_name']
        itemname = schema.get_localized_item_name(item['item_name'])
        if 'equip_region' in item:
            if isinstance(item['equip_region'], dict): # Valve are silly and on rare occasions put multiple regions in this field
                for region in item['equip_region']:
                    if region != 'hat':
                        add_region(itemname, region.lower())
            else:
                if item['equip_region'] != 'hat':
                    add_region(itemname, item['equip_region'].lower())
        elif 'equip_regions' in item:
            regions = item['equip_regions']
            if isinstance(regions, basestring): # Valve are also silly because sometimes they put a single region string here
                if regions != 'hat':
                    add_region(itemname, regions.lower())
            else:
                for region in regions:
                    if region != 'hat':
                        add_region(itemname, region.lower())
        if 'prefab' in item:
            if item['prefab'] in prefabs:
                prefab = prefabs[item['prefab']]
                if 'equip_region' in prefab and prefab['equip_region'] != 'hat':
                    region = prefab['equip_region']
                    add_region(itemname, region)

### Some output fixes here ###
itemExceptions = ['First Place - ETF2L Highlander Tournament',
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
                  'UGC Highlander Steel Participant',
                  'ESL Season VI Division 1 1st Place',
                  'ESL Season VI Division 1 2nd Place',
                  'ESL Season VI Division 1 3rd Place',
                  'ESL Season VI Division 1 Participant',
                  'ESL Season VI Division 2 1st Place',
                  'ESL Season VI Division 2 2nd Place',
                  'ESL Season VI Division 2 3rd Place',
                  'ESL Season VI Division 2 Participant',
                  'ESL Season VI Division 3 1st Place',
                  'ESL Season VI Division 3 2nd Place',
                  'ESL Season VI Division 3 3rd Place',
                  'ESL Season VI Division 3 Participant',
                  'ESL Season VI Division 4 1st Place',
                  'ESL Season VI Division 4 2nd Place',
                  'ESL Season VI Division 4 3rd Place',
                  'ESL Season VI Division 4 Participant',
                  'ESL Season VI Division 5 1st Place',
                  'ESL Season VI Division 5 2nd Place',
                  'ESL Season VI Division 5 3rd Place',
                  'ESL Season VI Division 5 Participant',
                  'ESL Season VI Premier Division 1st Place',
                  'ESL Season VI Premier Division 2nd Place',
                  'ESL Season VI Premier Division 3rd Place',
                  'ESL Season VI Premier Division Participant',
                  'ESL Season VII Division 1 1st Place',
                  'ESL Season VII Division 1 2nd Place',
                  'ESL Season VII Division 1 3rd Place',
                  'ESL Season VII Division 2 1st Place',
                  'ESL Season VII Division 2 2nd Place',
                  'ESL Season VII Division 2 Participant',
                  'ESL Season VII Division 3 Participant',
                  'ESL Season VII Division 4 1st Place',
                  'ESL Season VII Division 4 2nd Place',
                  'ESL Season VII Division 4 3rd Place',
                  'ESL Season VII Division 4 Participant',
                  'ESL Season VII Division 5 1st Place',
                  'ESL Season VII Division 5 2nd Place',
                  'ESL Season VII Division 5 3rd Place',
                  'ESL Season VII Division 5 Participant',
                  'ESL Season VII Premiership Division 1st Place',
                  'ESL Season VII Premiership Division 2nd Place',
                  'ESL Season VII Premiership Division 3rd Place',
                  'ESL Season VII Premiership Division Participant',
                  'AU Highlander Community League First Place',
                  'AU Highlander Community League Participant',
                  'AU Highlander Community League Second Place',
                  'AU Highlander Community League Third Place',
                  'ESH Ultiduo #1 Gold Medal',
                  'ESH Ultiduo #2 Gold Medal',
                  'ESH Ultiduo #3 Gold Medal',
                  'ESH Ultiduo #4 Gold Medal',
                  'ESH Ultiduo #5 Gold Medal',
                  'ESH Ultiduo #6 Gold Medal',
                  'ESH Ultiduo #7 Gold Medal',
                  'ETF2L 6v6 Division 1 Group Winner',
                  'ETF2L 6v6 Division 2 Group Winner',
                  'ETF2L 6v6 Division 3 Group Winner',
                  'ETF2L 6v6 Division 4 Group Winner',
                  'ETF2L 6v6 Division 5 Group Winner',
                  'ETF2L 6v6 Division 6 Group Winner',
                  'ETF2L 6v6 Division 1 Group Winner',
                  'ETF2L 6v6 Premier Division Bronze Medal',
                  'ETF2L 6v6 Premier Division Gold Medal',
                  'ETF2L 6v6 Premier Division Silver Medal',
                  'ETF2L Highlander Division 1 Bronze Medal',
                  'ETF2L Highlander Division 1 Gold Medal',
                  'ETF2L Highlander Division 1 Group Winner',
                  'ETF2L Highlander Division 1 Silver Medal',
                  'ETF2L Highlander Division 2 Group Winner',
                  'ETF2L Highlander Division 3 Group Winner',
                  'ETF2L Highlander Division 4 Group Winner',
                  'ETF2L Highlander Division 5 Group Winner',
                  'ETF2L Highlander Division 6 Group Winner',
                  'ETF2L Highlander Premier Division Bronze Medal',
                  'ETF2L Highlander Premier Division Gold Medal',
                  'ETF2L Highlander Premier Division Silver Medal',
                  'ETF2L Ultiduo #1 Gold Medal',
                  'ETF2L Ultiduo #2 Gold Medal',
                  'ETF2L Ultiduo #3 Gold Medal',
                  'ETF2L Ultiduo #4 Gold Medal',
                  'OWL 10 Division 2 First Place',
                  'OWL 10 Division 2 Participant',
                  'OWL 10 Division 2 Second Place',
                  'OWL 10 Division 2 Third Place',
                  'OWL 10 Division 3 First Place',
                  'OWL 10 Division 3 Participant',
                  'OWL 10 Division 3 Second Place',
                  'OWL 10 Division 3 Third Place',
                  'OWL 10 Division 4 First Place',
                  'OWL 10 Division 4 Participant',
                  'OWL 10 Division 4 Second Place',
                  'OWL 10 Division 4 Third Place',
                  'OWL 10 Division 5 First Place',
                  'OWL 10 Division 5 Participant',
                  'OWL 10 Division 5 Second Place',
                  'OWL 10 Division 5 Third Place',
                  'OWL 10 Division 6 First Place',
                  'OWL 10 Division 6 Participant',
                  'OWL 10 Division 6 Second Place',
                  'OWL 10 Division 6 Third Place',
                  'OWL 10 Premier Division First Place',
                  'OWL 10 Premier Division Participant',
                  'OWL 10 Premier Division Second Place',
                  'OWL 10 Premier Division Third Place',
                  'Ready Steady Pan Participant',
                  'Ready Steady Pan First Place',
                  'Ready Steady Pan Second Place',
                  'Ready Steady Pan Third Place',
                  'Ready Steady Pan Tournament Helper',
                  'Tournament Medal',
                  'UGC 6vs6 European Participant',
                  'UGC 6vs6 Platinum Participant',
                  'UGC 6vs6 Silver Participant',
                  'UGC 6vs6 Steel Participant',
                  'UGC Highlander 1st Place',
                  'UGC Highlander 1st Place Gold',
                  'UGC Highlander 1st Place Iron',
                  'UGC Highlander 1st Place Platinum',
                  'UGC Highlander 1st Place Silver',
                  'UGC Highlander 1st Place Steel',
                  'UGC Highlander 2nd Place',
                  'UGC Highlander 2nd Place Gold',
                  'UGC Highlander 2nd Place Iron',
                  'UGC Highlander 2nd Place Platinum',
                  'UGC Highlander 2nd Place Silver',
                  'UGC Highlander 2nd Place Steel',
                  'UGC Highlander 3rd Place',
                  'UGC Highlander 3rd Place Gold',
                  'UGC Highlander 3rd Place Iron',
                  'UGC Highlander 3rd Place Platinum',
                  'UGC Highlander 3rd Place Silver',
                  'UGC Highlander 3rd Place Steel',
                  'UGC Highlander Gold Participant',
                  'UGC Highlander Iron Participant',

                  'Voodoo-Cursed Soul',
                  'Demobot Armor',
                  'Engineerbot Armor',
                  'Heavybot Armor',
                  'Pyrobot Armor',
                  'Scoutbot Armor',
                  'Sentrybuster',
                  'Sniperbot Armor',
                  'Soldierbot Armor',
                  'Spybot Armor',
                  'Medicbot Chariot'
                  ]

if 'medal' in regionsDict:
    regionsDict['medal'].append('Tournament Medal - ETF2L Highlander Tournament')
    regionsDict['medal'].append('Tournament Medal - GWJ Tournament')
    regionsDict['medal'].append('Tournament Medal - UGC Highlander Tournament')

for region in regionsDict:
    # Fix Essential Accessories
    if 'The Essential Accessories' in regionsDict[region]:
        regionsDict[region].remove('The Essential Accessories')
        regionsDict[region].append('Essential Accessories')

    for item in itemExceptions:
        if item in regionsDict[region]:
            regionsDict[region].remove(item)

regionsDict = sorted(regionsDict.items())
output = open('equipregions.txt', 'wb')

for regionname, regionitems in regionsDict:
    regionitems.sort(key=lambda s: (s.lower(), s))
    output.write('! {{item name|er ' + regionname + '}}')
    n = 1
    for item in regionitems:
        item = item.encode('utf-8')
        if len(regionitems) == 1:
            if item == 'Halloween Masks':
                output.write('\n| style="font-weight:bold; font-size:0.95em;" | [[File:Heavy Mask.png|40px]] [[Halloween Masks{{if lang}}|{{item name|Halloween Masks}}]]')
            else:
                output.write('\n| style="font-weight:bold; font-size:0.95em;" | {{item nav link|' + item + '}}')
        elif n == 1:
            if item == 'Halloween Masks':
                output.write('\n| style="font-weight:bold; font-size:0.95em;" | [[File:Heavy Mask.png|40px]] [[Halloween Masks{{if lang}}|{{item name|Halloween Masks}}]]<!--')
            else:
                output.write('\n| style="font-weight:bold; font-size:0.95em;" | {{item nav link|' + item + '}}<!--')
            n += 1
        elif n == len(regionitems):
            if item == 'Halloween Masks':
                output.write('\n --><br />[[File:Heavy Mask.png|40px]] [[Halloween Masks{{if lang}}|{{item name|Halloween Masks}}]]')
            else:
                output.write('\n --><br />{{item nav link|' + item + '}}')
        else:
            if item == 'Halloween Masks':
                output.write('\n --><br />[[File:Heavy Mask.png|40px]] [[Halloween Masks{{if lang}}|{{item name|Halloween Masks}}]]<!--')
            else:
                output.write('\n --><br />{{item nav link|' + item + '}}<!--')
            n += 1
    output.write('\n|-\n')
output.write('|}')
output.close()
print '\nDone, printed to equipregions.txt'