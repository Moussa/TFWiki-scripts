#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import sys
import wikitools
import steam
from config import config

print('Fetching schema...')
steam.api.key.set(config['steam_api_key'])
schema = steam.items.schema('440', 'en_US')

wiki = wikitools.wiki.Wiki(config['tf2']['wikiApi'])
wiki.login(config['tf2']['wikiUsername'], config['tf2']['wikiPassword'])

def save_current_schema_ids():
	_ids = get_schema_ids()

	with open('schema_state.txt', 'wb') as f:
		for _id in _ids:
			f.write('{0}\n'.format(_id))

def get_schema_ids():
	return [item.schema_id for item in schema]

def get_current_schema_state():
	_ids = []
	with open('schema_state.txt', 'rb') as f:
		for line in f:
			_ids.append(int(line.strip()))

	return _ids

def get_new_item_ids():
	previous_ids = get_current_schema_state()
	current_ids = get_schema_ids()

	return [_id for _id in current_ids if _id not in previous_ids]

def get_item_type(item):
	slots = {'hat': ['head'],
             'misc': ['misc'],
             'weapon': ['melee', 'primary', 'pda2', 'secondary', 'building', 'pda'],
             'action': ['action']
             }
	item_slot = item.slot_name

	for slot in slots:
		if item_slot in slots[slot]:
			return slot

def hat_or_misc_template():
	return """{{{{ra}}}}
{{{{stub}}}}
{{{{Item infobox
| type               = {type}
| image              = {item_name}.png
| team-colors        = 
| used-by            = {class_links}
| released           = {patch_string}
| availability       = 
| trade              = yes
| gift               = {can_gift}
| paint              = 
| rename             = yes
| numbered           = 
| loadout            = yes
  | quality          = unique
  | level            = Level {min_level}-{max_level} {level_type}
  | item-description = {item_description}
}}}}

{class_navs}"""

def create_page(page_title, template):
	page = wikitools.page.Page(wiki, page_title)

	if page.exists:
		print('Skipping, page already exists')
	else:
		page.edit(template, summary=u'Creating skeleton page for new item', minor=True, bot=False, skipmd5=True, timeout=60)

def generate_pages(new_ids):
	for _id in new_ids:
		item = schema.__getitem__(_id)
		print("Processing '{0}'".format(item.name))

		used_by_classes = item.equipable_classes
		item_type = get_item_type(item)

		template = None
		if item_type == 'hat' or item_type == 'misc':
			template = hat_or_misc_template().format(type = item_type,
                                                     item_name = item.name.replace(' ', '_'),
                                                     class_links = ", ".join(['[[{0}]]'.format(_class.capitalize()) for _class in item.equipable_classes]),
                                                     patch_string = time.strftime("{{{{Patch name|%m|%d|%Y}}}}", time.localtime(time.time() - (6*60*60))),
                                                     can_gift = "yes" if item.craftable else "no",
                                                     item_description = item.description if item.description else "",
                                                     min_level = item.min_level,
                                                     max_level = item.max_level,
                                                     level_type = item.type,
                                                     class_navs = "\n".join(['{{{{{0} Nav}}}}'.format(_class.capitalize()) for _class in item.equipable_classes])
                                                     )
		elif item_type == 'weapon':
			pass
		elif item_type == 'action':
			pass

		if template:
			create_page(item.name, template)

	# Save new current schema state
	save_current_schema_ids()

if __name__ == '__main__':
	print('Fetching list of new item ids')
	new_ids = get_new_item_ids()

	if len(new_ids) == 0:
		print('No new item ids')
		sys.exit()

	print('{0} new items'.format(len(new_ids)))
	print('Creating pages...')

	generate_pages(new_ids)