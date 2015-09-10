# -*- coding: utf-8 -*-
# Generates the equip regions table found at
# http://wiki.tf/Template:Equip_region_table on the wiki

import re, copy
from vdfparser import VDF

schema = VDF()
items = schema.get_items()
prefabs = schema.get_prefabs()
allitems = dict(items, **prefabs)

er_none = {'misc', 'valve misc', 'base_misc', 'base_hat', 'ash_remains base_misc'} # A list of prefabs which can be defined for an item which has no equip region.
regionsDict = {}
TF_classes = ['scout', 'soldier', 'pyro', 'demoman', 'heavy', 'engineer', 'medic', 'sniper', 'spy', 'allclass'] # This table is dynamic, which is to say none of the rest of the code explicitly relies on the order or size of it.
verbose = False

def add_region(itemname, TF_classlist, region):
    for TF_class in TF_classes:
        if re.search('^'+TF_class, region):
            region = '{{void|'+str(TF_classes.index(TF_class))+'}}'+region
        if re.search('^demo', region):
            region = '{{void|'+str(TF_classes.index('demoman'))+'}}'+region
        if re.search('^medigun', region):
            region = '{{void|'+str(TF_classes.index('medic'))+'}}'+region
        if region == 'none':
            region = '{{void}}none'
    if len(TF_classlist) == len(TF_classes)-1:
        TF_classlist = {'allclass': '1'} # Mimics the style of the actual items_game
    if region not in regionsDict:
        regionsDict[region] = {}
        for TF_class in TF_classes:
            regionsDict[region][TF_class] = []
        if verbose:
            print 'Added region', region
    for TF_class in TF_classlist:
        if itemname not in regionsDict[region][TF_class]:
            regionsDict[region][TF_class].append(itemname)

print 'Adding items...'
for item in allitems:
    item = allitems[item]
    if 'item_name' in item:
        TF_classlist = {}
        if 'used_by_classes' in item:
            TF_classlist = item['used_by_classes']
        itemname = schema.get_localized_item_name(item['item_name'])
        if verbose:
            print 'Processing', itemname
        if 'equip_region' in item:
            if isinstance(item['equip_region'], dict): # Valve are silly and on rare occasions put multiple regions in this field
                for region in item['equip_region']:
                    if region != 'hat':
                        add_region(itemname, TF_classlist, region.lower())
            else:
                if item['equip_region'] != 'hat':
                    add_region(itemname, TF_classlist, item['equip_region'].lower())
        elif 'equip_regions' in item:
            regions = item['equip_regions']
            if isinstance(regions, basestring): # Valve are also silly because sometimes they put a single region string here
                if regions != 'hat':
                    add_region(itemname, TF_classlist, regions.lower())
            else:
                for region in regions:
                    if region != 'hat':
                        add_region(itemname, TF_classlist, region.lower())
        elif 'prefab' in item:
            if isinstance(item['prefab'], list): # Valve are even sillier because sometimes they put their own name in the prefabs list
                item['prefab'] = item['prefab'][1]
            if item['prefab'] in prefabs:
                prefab = prefabs[item['prefab']]
                if 'used_by_classes' in prefab:
                    TF_classlist.update(prefab['used_by_classes'])
                if 'equip_region' in prefab and prefab['equip_region'] != 'hat':
                    region = prefab['equip_region']
                    add_region(itemname, TF_classlist, region)
            if item['prefab'] in er_none:
                if verbose:
                    print 'Item', itemname, 'has no equip region. Prefab is:', item['prefab']
                add_region(itemname, TF_classlist, 'none')

### Begin output fixes ###
itemExceptions = [ # These are keywords which, if present, will make the item ignored.
    '(Scout|Soldier|Pyro|Demo|Heavy|Engineer|Medic|Sniper|Spy)bot Armor',
    'Medicbot Chariot',
    'Sentrybuster',
    'Spine-(Cooling|Tingling|Twisting) Skull', # These are different styles
    'Voodoo-Cursed Soul',

    'Arms Race',
    'Asiafortress Cup',
    'AU Highlander Community League',
    'BETA LAN',
    'ESH',
    'ESL',
    'ETF2L',
    'FBTF',
    'Florida LAN',
    'GA\'lloween',
    'Gamers Assembly',
    'Gamers With Jobs',
    'InfoShow TF2',
    'LBTF2',
    'OSL.tf',
    'OWL',
    'Ready Steady Pan',
    'RETF2',
    'TF2Connexion',
    'Tumblr Vs Reddit',
    'UGC',
]

print 'Removing items...'
for region in regionsDict:
    if 'The Essential Accessories' in regionsDict[region]['scout']:
        regionsDict[region]['scout'].remove('The Essential Accessories')
        regionsDict[region]['scout'].append('Essential Accessories')
    newlist = copy.deepcopy(regionsDict[region])
    for TF_class in TF_classes:
        for item in regionsDict[region][TF_class]:
            for exception in itemExceptions:
                if re.search(exception, item):
                    newlist[TF_class].remove(item)
                    if verbose:
                        print item, 'discarded, matched filter', exception
                    break
    regionsDict[region] = newlist
### End output fixes ###

regionsDict = sorted(regionsDict.items())
output = open('equipregions.txt', 'wb')

print 'Writing output...'
for regionname, regionitems in regionsDict:
    ### Begin style modifications ###
    # If there are no all-class items, that row is left out.
    # If there are only items for a particular class, only list that class.
    # If there are only items for allclass, only list allclass.
    specificClass = None
    noAllclass = len(regionitems['allclass']) == 0
    length = 0
    for TF_class in TF_classes:
        if re.search(TF_class, regionname):
            specificClass = TF_class
        if re.search('demo', regionname): # Valve are stupid and call things 'demo' when they mean 'demoman'
            specificClass = 'demoman'
        if re.search('medigun', regionname): # Valve are also stupid and call things 'medigun' when they mean 'medic'
            specificClass = 'medic'
        if TF_class != 'allclass':
            length += len(regionitems[TF_class])
    if length == 0: # If there are no items for any class, there must be items for only allclass
        specificClass = 'allclass'
    ### End style modifications ###
    
    output.write('!')
    if not noAllclass and not specificClass:
        output.write(' rowspan="2" |')
    output.write(' {{item name|er ' + regionname + '}}')
    blankLines = 0
    for TF_class in TF_classes:
        isAllclass = (TF_class == 'allclass')
        if isAllclass and noAllclass:
            continue
        if specificClass and TF_class != specificClass:
            continue
        regionitems[TF_class].sort(key=lambda s: (s.lower(), s))
        if not specificClass:
            if isAllclass:
                output.write('\n|-')
            else: # This block handles merging multiple blank boxes.
                if len(regionitems[TF_class]) == 0:
                    blankLines += 1
                if TF_class == 'spy' or len(regionitems[TF_class]) > 0:
                    output.write('\n|')
                    if blankLines not in [0,1]:
                        output.write(' colspan="{}" |'.format(blankLines))
                    if blankLines != 0 and len(regionitems[TF_class]) > 0:
                        output.write('\n|')
                    blankLines = 0
        
        for n in range(0, len(regionitems[TF_class])):
            item = regionitems[TF_class][n].encode('utf-8')
            if n != 0 and len(regionitems[TF_class]) != 1:
                output.write('<!--\n-->')
                if not isAllclass and not specificClass:
                    output.write('<br />')
            if n == 0:
                if isAllclass or (specificClass == TF_class):
                    output.write('\n| colspan="9" align="center"')
                output.write(' style="font-weight:bold; font-size:0.95em;" | ')
            # Items which need custom images go here
            if item == 'Halloween Masks':
                output.write('[[File:Heavy Mask.png|40px]] [[Halloween Masks{{if lang}}|{{item name|Halloween Masks}}]]')
            else:
                output.write('{{item nav link|' + item + '|small=yes}}')
    output.write('\n|-\n')
output.write('|}')
output.close()
print 'Done, printed to equipregions.txt'
