import os
from vdfparser import VDF
schema = VDF()
items = schema.get_items()
prefabs = schema.get_prefabs()
allitems = dict(items, **prefabs)
max1 = 0
max2 = 0
modelmap = {}
TF_classes = ['scout', 'soldier', 'pyro', 'demoman', 'heavy', 'engineer', 'medic', 'sniper', 'spy', 'multi-class', 'all class']
item_slots = ['primary', 'secondary', 'melee', 'pda', 'pda2', 'building', 'cosmetic']
data = [[{} for __ in item_slots] for _ in TF_classes]
rootdir = "/Volumes/BOOTCAMP/Users/Joseph Blackman/Desktop/tf2_misc_dir/models/decompiled 0.19"
for k in allitems.keys():
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
		if file[-13:] == 'reference.smd':
			modelname = file[:-14]
		else:
			if file[-9:-5] == '_lod':
				file = file[:-9]
			if file[-9:] == 'reference':
				file = file[:-10]
			parts = file.split('_')
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
		if len(name) == 2:
			propername += '|style='+schema.get_localized_item_name(name[1])
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
		if item_slot < 6 and max1 < count:
			max1 = count
		if item_slot == 6 and max2 < count:
			max2 = count
		if propername not in data[TF_class][item_slot]:
			data[TF_class][item_slot][propername] = [count, count]
		elif data[TF_class][item_slot][propername][0] < count:
			data[TF_class][item_slot][propername][0] = count
		elif data[TF_class][item_slot][propername][1] > count:
			data[TF_class][item_slot][propername][1] = count

print 'Done processing, writing to file...'

g = open('LODTable_weapons.txt', 'wb')
g.write('''<includeonly>{| class="wikitable sortable grid"
! class="header" width="7%" | Class
! class="header" width="7%" | Slot
! class="header" width="18%" | Item
! class="header" width="32%" | Highest quality LOD (polycount)
! class="header" width="32%" | Lowest quality LOD (polycount)
! class="header" width="4%" | LOD Efficiency
|-
''')
h = open('LODTable_cosmetics.txt', 'wb')
h.write('<includeonly>')
for i in range(len(TF_classes)):
	count = 0
	for j in range(len(item_slots[:6])):
		count += len(data[i][j])
	g.write('|rowspan="'+str(count)+'" data-sort-value="'+str(i)+'"|'+TF_classes[i].capitalize()+'\n')
	for j in range(len(item_slots[:6])):
		if len(data[i][j]) != 0:
			g.write('|rowspan="'+str(len(data[i][j]))+'" data-sort-value="'+str(j)+'"|'+item_slots[j].capitalize()+'\n')
		for k in sorted(data[i][j].keys()):
			g.write('{{LODTable/core|max={{{max}}}|'+k.encode('utf-8')+'|'+str(data[i][j][k][0]))
			if data[i][j][k][0] != data[i][j][k][1]:
				g.write('|'+str(data[i][j][k][1]))
			g.write('}}\n')
	if len(data[i][6]) != 0:
		h.write('=== '+TF_classes[i].capitalize()+''' ===
{| class="wikitable sortable grid collapsible collapsed"
! class="header" width="20%" | Item
! class="header" width="38%" | Highest quality LOD (polycount)
! class="header" width="38%" | Lowest quality LOD (polycount)
! class="header" width="4%" | LOD Efficiency
|-
''')
	for k in sorted(data[i][6].keys()):
		h.write('{{LODTable/core|max={{{max}}}|'+k.encode('utf-8')+'|'+str(data[i][6][k][0]))
		if data[i][6][k][0] != data[i][6][k][1]:
			h.write('|'+str(data[i][6][k][1]))
		h.write('}}\n')
	if len(data[i][6]) != 0:
		h.write('|}\n')
g.write('|}'+'''</includeonly><noinclude>
{{LODTable/weapons|max='''+str(max1)+'''}}
</noinclude>''')
g.close()
print 'Done, weapons written to LODTable_weapons.txt'
h.write('|}'+'''</includeonly><noinclude>
{{LODTable/cosmetics|max='''+str(max2)+'''}}
</noinclude>''')
h.close()
print 'Cosmetics written to LODTable_cosmetics.txt'