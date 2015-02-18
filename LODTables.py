import os
from vdfparser import VDF
schema = VDF()
items = schema.get_items()
prefabs = schema.get_prefabs()
allitems = dict(items, **prefabs)
max = [0]*14
modelmap = {}
allitems.update({ # Extra data for engineer buildings
	'Sentry Gun Level 1': {
		'model_world': 'models/buildings/sentry1.mdl',
		'item_name': '#TF_Object_Sentry',
		'level': '1',
		'used_by_classes': {
			'engineer': '1'
		},
		'item_slot': 'building2'
	},
	'Sentry Gun Level 2': {
		'model_world': 'models/buildings/sentry2_optimized.mdl',
		'item_name': '#TF_Object_Sentry',
		'level': '2',
		'used_by_classes': {
			'engineer': '1'
		},
		'item_slot': 'building2'
	},
	'Sentry Gun Level 3': {
		'model_world': 'models/buildings/sentry3_optimized.mdl',
		'item_name': '#TF_Object_Sentry',
		'level': '3',
		'used_by_classes': {
			'engineer': '1'
		},
		'item_slot': 'building2'
	},
	'Dispenser Level 1': {
		'model_world': 'models/buildings/dispenser_toolbox.mdl',
		'item_name': '#TF_Object_Dispenser',
		'level': '1',
		'used_by_classes': {
			'engineer': '1'
		},
		'item_slot': 'building2'
	},
	'Dispenser Level 2': {
		'model_world': 'models/buildings/dispenser_lvl2.mdl',
		'item_name': '#TF_Object_Dispenser',
		'level': '2',
		'used_by_classes': {
			'engineer': '1'
		},
		'item_slot': 'building2'
	},
	'Dispenser Level 3': {
		'model_world': 'models/buildings/dispenser_lvl3.mdl',
		'item_name': '#TF_Object_Dispenser',
		'level': '3',
		'used_by_classes': {
			'engineer': '1'
		},
		'item_slot': 'building2'
	},
	'Teleporter': {
		'model_world': 'models/buildings/teleporter.mdl',
		'item_name': '#TF_Object_Tele',
		'used_by_classes': {
			'engineer': '1'
		},
		'item_slot': 'building2'
	},
	'Scout': {
		'model_world': 'models/player/scout.mdl',
		'model_player': 'models/player/scout_morphs_high.mdl',
		'item_name': "#TF_class_Name_Scout",
		'used_by_classes': {
			'scout': '1'
		},
		'item_slot': 'class'
	},
	'Soldier': {
		'model_world': 'models/player/soldier.mdl',
		'model_player': 'models/player/soldier_morphs_high.mdl',
		'item_name': "#TF_class_Name_Soldier",
		'used_by_classes': {
			'soldier': '1'
		},
		'item_slot': 'class'
	},
	'Pyro': {
		'model_world': 'models/player/pyro.mdl',
		'model_player': 'models/player/pyro_morphs_high.mdl',
		'item_name': "#TF_class_Name_Pyro",
		'used_by_classes': {
			'pyro': '1'
		},
		'item_slot': 'class'
	},
	'Demoman': {
		'model_world': 'models/player/demo.mdl',
		'model_player': 'models/player/demo_morphs_high.mdl',
		'item_name': "#TF_class_Name_Demoman",
		'used_by_classes': {
			'demoman': '1'
		},
		'item_slot': 'class'
	},
	'Heavy': {
		'model_world': 'models/player/heavy.mdl',
		'model_player': 'models/player/heavy_morphs_high.mdl',
		'item_name': "#TF_class_Name_HWGuy",
		'used_by_classes': {
			'heavy': '1'
		},
		'item_slot': 'class'
	},
	'Engineer': {
		'model_world': 'models/player/engineer.mdl',
		'model_player': 'models/player/engineer_morphs_high.mdl',
		'item_name': "#TF_class_Name_Engineer",
		'used_by_classes': {
			'engineer': '1'
		},
		'item_slot': 'class'
	},
	'Medic': {
		'model_world': 'models/player/medic.mdl',
		'model_player': 'models/player/medic_morphs_high.mdl',
		'item_name': "#TF_class_Name_Medic",
		'used_by_classes': {
			'medic': '1'
		},
		'item_slot': 'class'
	},
	'Sniper': {
		'model_world': 'models/player/sniper.mdl',
		'model_player': 'models/player/sniper_morphs_high.mdl',
		'item_name': "#TF_class_Name_Sniper",
		'used_by_classes': {
			'sniper': '1'
		},
		'item_slot': 'class'
	},
	'Spy': {
		'model_world': 'models/player/spy.mdl',
		'model_player': 'models/player/spy_morphs_high.mdl',
		'item_name': "#TF_class_Name_Spy",
		'used_by_classes': {
			'spy': '1'
		},
		'item_slot': 'class'
	},
})
TF_classes = ['scout', 'soldier', 'pyro', 'demoman', 'heavy', 'engineer', 'medic', 'sniper', 'spy', 'multi-class', 'all classes']
item_slots = ['primary', 'secondary', 'melee', 'pda', 'pda2', 'building', 'cosmetic', 'building2', 'class']
data = [[{} for __ in item_slots] for _ in TF_classes]
rootdir = "/Volumes/BOOTCAMP/Users/Joseph Blackman/Desktop/tf2_misc_dir/models/decompiled 0.19"
for k in allitems.keys():
	# Fix for some broken weapons
	if 'prefab' in allitems[k] and 'extra_wearable' not in allitems[k]:
		prefab = allitems[k]['prefab']
		prefab = prefab.split(' ')[-1]
		if prefab.split(' ')[:7] == 'weapon_' or prefab in ['holy_mackerel', 'axtinguisher', 'buff_banner', 'sandvich', 'ubersaw', 'frontier_justice', 'huntsman', 'ambassador']:
			if prefab == 'weapon_shotgun':
				prefab = 'weapon_shotgun_multiclass'
			allitems[k]['item_slot'] = prefabs[prefab]['item_slot']
			allitems[k]['used_by_classes'] = prefabs[prefab]['used_by_classes']
	# Get model names
	if 'model_world' in allitems[k]:
		modelname = allitems[k]['model_world'].split('/')[-1][:-4]
		modelmap[modelname] = [k]
	if 'model_player' in allitems[k]:
		modelname = allitems[k]['model_player'].split('/')[-1][:-4]
		modelmap[modelname] = [k]
	if 'model_player_per_class' in allitems[k]:
		for TF_class in allitems[k]['model_player_per_class'].keys():
			modelname = allitems[k]['model_player_per_class'][TF_class].split('/')[-1][:-4]
			modelmap[modelname] = [k]
	if 'visuals' in allitems[k]:
		if 'styles' in allitems[k]['visuals']:
			for s in allitems[k]['visuals']['styles'].values():
				if 'model_player' in s:
					modelname = s['model_player'].split('/')[-1][:-4]
					modelmap[modelname] = [k, s['name']]
				if 'model_player_per_class' in s:
					for TF_class in allitems[k]['model_player_per_class'].keys():
						modelname = s['model_player_per_class'][TF_class].split('/')[-1][:-4]
						modelmap[modelname] = [k, s['name']]

print 'Done pre-processing'

for root, subFolders, files in os.walk(rootdir):
	for file in files:
		if file[-4:] != '.smd':
			continue
		if file[-11:] == 'physics.smd':
			continue
		if file[-13:] == 'bodygroup.smd':
			continue
		if file == 'idle.smd':
			continue
		f = open(os.path.join(root, file), 'rb').read()
		file = file[:-4] # Cuts .smd
		if file[-13:] == 'reference':
			modelname = file[:-14]
		else:
			if file[-5:-1] == '_lod':
				file = file[:-5]
			if file[-10:] == '_reference':
				file = file[:-10]
			parts = file.split('_')
			if len(parts) > 5 and parts[5][:5] == 'shell': # Exception for a badly named file
				continue
			modelname = parts[0]
			for p in range(1,len(parts)):
				if parts[p] == parts[0]:
					for q in range(1, p):
						modelname += '_'+parts[q]
					break
				if p == len(parts)-1:
					modelname = file
		if modelname not in modelmap:
			continue
		name = modelmap[modelname]
		if 'vision_filter_flags' in allitems[name[0]]: # Romevision bot armor
			continue
		propername = schema.get_localized_item_name(allitems[name[0]]['item_name'])
		if propername == 'The Essential Accessories':
			propername = 'Essential Accessories'
		elif propername == 'Teleporter':
			propername = 'Teleporters'
		if len(name) == 2: # Styles add-in
			propername += '|style='+schema.get_localized_item_name(name[1])
		if 'level' in allitems[name[0]]: # Hack for engineer buildings
			propername += '|level='+allitems[name[0]]['level']

		lines = f.split('\r\n')
		count = 0
		for i in range(len(lines)):
			if lines[i] == 'triangles':
				count = (len(lines) - i - 3)/4
				break
		if count == 0: # Non-models don't have 'triangles' in them, so we ignore them
			continue
		if 'used_by_classes' not in allitems[name[0]]:
			continue
		usedby = allitems[name[0]]['used_by_classes']
		if len(usedby) == 1:
			TF_class = TF_classes.index(usedby.keys()[0])
		elif len(usedby) == 9: # All class
			TF_class = 10
		else: # Multi class
			TF_class = 9
		if 'item_slot' in allitems[name[0]]: # Default, used for weapons and new cosmetic listings.
			slot = allitems[name[0]]['item_slot']
		elif 'prefab' in allitems[name[0]]:
			slot = 'cosmetic'
		if slot in ['misc', 'head']: # Old cosmetic listings
			slot = 'cosmetic'
		if slot not in item_slots:
			continue
		item_slot = item_slots.index(slot)
		if item_slot < 6 and max[0] < count:
			max[0] = count
		if item_slot == 6 and max[TF_class+1] < count:
			max[TF_class+1] = count
		if item_slot == 7 and max[12] < count:
			max[12] = count
		if item_slot == 8 and max[13] < count:
			max[13] = count
		if propername not in data[TF_class][item_slot]:
			data[TF_class][item_slot][propername] = [count, count]
		elif data[TF_class][item_slot][propername][0] < count:
			data[TF_class][item_slot][propername][0] = count
		elif data[TF_class][item_slot][propername][1] > count:
			data[TF_class][item_slot][propername][1] = count

print 'Done processing, writing to file...'

f = open('LODTable.txt', 'wb')
f.write('''
== {{Item name|Weapons}} ==
{| class="wikitable sortable grid"
! class="header" width="10%" | Class
! class="header" width="7%" | Slot
! class="header" width="17%" | Item
! class="header" width="32%" | Highest quality LOD (polycount)
! class="header" width="32%" | Lowest quality LOD (polycount)
! class="header" width="2%" | LOD Efficiency
|-
''')
for i in range(len(TF_classes)):
	count = 0
	for j in range(len(item_slots[:6])):
		count += len(data[i][j])
	f.write('|rowspan="'+str(count)+'" data-sort-value="'+str(i)+'"| {{class link|'+TF_classes[i]+'}}\n')
	for j in range(len(item_slots[:6])):
		if len(data[i][j]) != 0:
			f.write('|rowspan="'+str(len(data[i][j]))+'" data-sort-value="'+str(j)+'"|{{Item name|'+item_slots[j]+'}}\n')
		for k in sorted(data[i][j].keys()):
			f.write('{{LODTable/core|max='+str(max[0])+'|'+k.encode('utf-8')+'|'+str(data[i][j][k][0]))
			if data[i][j][k][0] != data[i][j][k][1]:
				f.write('|'+str(data[i][j][k][1]))
			f.write('}}\n')
f.write('''|}

== {{Item name|Cosmetics}} ==
;Key
:<span style="background:#93aecf; padding:0em 2em;">&nbsp;</span> Unoptimized
:<span style="background:#F3A957; padding:0em 2em;">&nbsp;</span> Optimized
''')
for i in range(len(TF_classes)):
	if len(data[i][6]) != 0:
		f.write('=== {{Dictionary/classes/'+TF_classes[i]+'''}} ===
{| class="wikitable sortable grid collapsible collapsed"
! class="header" width="20%" | Item
! class="header" width="38%" | Highest quality LOD (polycount)
! class="header" width="38%" | Lowest quality LOD (polycount)
! class="header" width="2%" | LOD Efficiency
|-
''')
	for k in sorted(data[i][6].keys()):
		f.write('{{LODTable/core|max='+str(max[i+1])+'|'+k.encode('utf-8')+'|'+str(data[i][6][k][0]))
		if data[i][6][k][0] != data[i][6][k][1]:
			f.write('|'+str(data[i][6][k][1]))
		f.write('}}\n')
	f.write('|}\n')
f.write('''

== {{Item name|Buildings}} ==
;Key
:<span style="background:#93aecf; padding:0em 2em;">&nbsp;</span> Unoptimized
:<span style="background:#F3A957; padding:0em 2em;">&nbsp;</span> Optimized

{| class="wikitable sortable grid"
! class="header" width="10%" | Class
! class="header" width="18%" | Item
! class="header" width="35%" | Highest quality LOD (polycount)
! class="header" width="35%" | Lowest quality LOD (polycount)
! class="header" width="2%" | LOD Efficiency
|-
''')
for i in range(len(TF_classes)):
	if len(data[i][7]) == 0:
		continue
	f.write('|rowspan="'+str(len(data[i][7]))+'" data-sort-value="'+str(i)+'"| {{class link|'+TF_classes[i]+'}}\n')
	for k in sorted(data[i][7].keys()):
		f.write('{{LODTable/core|max='+str(max[12])+'|'+k.encode('utf-8')+'|'+str(data[i][7][k][0]))
		if data[i][7][k][0] != data[i][7][k][1]:
			f.write('|'+str(data[i][7][k][1]))
		f.write('}}\n')
f.write('''|}

== {{Common string|Classes}} ==
{| class="wikitable sortable grid"
! class="header" width="10%" | Class
! class="header" width="42%" | Highest quality LOD (polycount)
! class="header" width="42%" | Lowest quality LOD (polycount)
! class="header" width="2%" | LOD Efficiency
|-
''')
for i in range(len(TF_classes)):
	if len(data[i][8]) == 0:
		continue
	for k in sorted(data[i][8].keys()):
		f.write('{{LODTable/core|max='+str(max[13])+'|'+k.encode('utf-8')+'|'+str(data[i][8][k][0]))
		if data[i][8][k][0] != data[i][8][k][1]:
			f.write('|'+str(data[i][8][k][1]))
		f.write('}}\n')
f.write('|}')

f.close()

print 'Done, wrote to LODTables.txt'
