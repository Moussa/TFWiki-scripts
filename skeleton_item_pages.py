#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2
import time
import os
import sys
import wikitools
import steam
from skeleton_config import config

print('Fetching schema...')
steam.api.key.set(config['steam_api_key'])
schema = steam.items.schema('440', 'en_US')

wiki = wikitools.wiki.Wiki(config['wikiApi'])
wiki.login(config['wikiUsername'], config['wikiPassword'])

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
            try:
                _ids.append(int(line.strip()))
            except:
                pass

    return _ids

def get_new_item_ids():
    previous_ids = get_current_schema_state()
    current_ids = get_schema_ids()

    return [_id for _id in current_ids if _id not in previous_ids]

def get_item_type(item):
    slots = {'cosmetic': ['head', 'misc'],
             'weapon': ['melee', 'primary', 'pda2', 'secondary', 'building', 'pda'],
             'action': ['action']
             }
    item_slot = item.slot_name

    for slot in slots:
        if item_slot in slots[slot]:
            return slot

def cosmetic_template():
    return """{{{{ra}}}}
{{{{stub}}}}
{{{{Item infobox
| type               = cosmetic
| image              = {item_name}.png
| team-colors        = 
| used-by            = {class_links}
| released           = {patch_string}
| availability       = 
| trade              = yes
| gift               = yes
| paint              = 
| rename             = yes
| numbered           = 
| loadout            = yes
  | quality          = unique
  | level            = Level {min_level}-{max_level} {level_type}
  | item-description = {item_description}
}}}}

The '''{proper_item_name}''' is a [[Cosmetic items|Cosmetic item]] for the {class_links}.

== Update history ==
'''{patch_string}'''
* The {proper_item_name} was added to the game.

{{{{HatNav}}}}
{class_navs}"""

def weapon_template():
    return """{{{{ra}}}}
{{{{stub}}}}
{{{{Item infobox
| type               = weapon
| image              = {item_name}.png
| hide-kill-icon     = 
| used-by            = {class_links}
| slot               = {slot}
| released           = {patch_string}
| availability       = 
| medieval           = 
| show-ammo          = 
| reload             = 
| trade              = yes
| gift               = 
| rename             = yes
| numbered           = 
| loadout            = yes
  | loadout-prefix   = none
  | level            = Level {level} {level_type}
  | item-description = {item_description}
}}}}

The '''{proper_item_name}''' is a [[weapon]] for the {class_links}.

== Update history ==
'''{patch_string}'''
* The {proper_item_name} was added to the game.

{{{{Allweapons Nav}}}}
{class_navs}"""

def create_page(page_title, template):
    page = wikitools.page.Page(wiki, page_title)

    if page.exists:
        print('Skipping, page already exists')
    else:
        page.edit(template, summary='Creating skeleton page for new item', minor=True, bot=False, skipmd5=True, timeout=60)

def upload_backpack_image(item_name, image_url, item_type):
    page = wikitools.page.Page(wiki, 'File:Backpack {0}.png'.format(item_name))

    if page.exists:
        print('Skipping, page already exists')
        return

    with open(item_name + '.png', 'wb') as tmp:
        tmp.write(urllib2.urlopen(image_url).read())

    backpack_image = wikitools.wikifile.File(wiki, 'File:Backpack {0}.png'.format(item_name))
    backpack_image.upload(fileobj=open(item_name + '.png', 'rb'), ignorewarnings=True, comment='')
    os.remove(item_name + '.png')

    page_content = """== Licensing ==
{{{{ExtractTF2}}}}

[[Category:Backpack images]]
[[Category:{type} images]]"""

    if item_type == 'cosmetic':
        page_content = page_content.format(type='Cosmetic')
    elif item_type == 'weapon':
        page_content = page_content.format(type='Weapon')
    elif item_type == 'action':
        page_content = page_content.format(type='Tool')

    backpack_page = wikitools.page.Page(wiki, 'File:Backpack {0}.png'.format(item_name))
    backpack_page.edit(page_content, summary='', minor=True, bot=False, skipmd5=True, timeout=60)

def generate_pages(new_ids):
    for _id in new_ids:
        item = schema.__getitem__(_id)
        print("Processing '{0}'".format(item.name))

        if item.equipable_classes != []:
            class_links = ", ".join(['[[{0}]]'.format(_class.capitalize()) for _class in item.equipable_classes])
            class_navs = "\n".join(['{{{{{0} Nav}}}}'.format(_class.capitalize()) for _class in item.equipable_classes])
        else:
            class_links = "[[Classes|All classes]]"
            class_navs = ""
        item_type = get_item_type(item)

        template = None
        if item_type == 'cosmetic':
            template = cosmetic_template().format(item_name = item.name.replace(' ', '_'),
                                                  proper_item_name = item.name,
                                                  class_links = class_links,
                                                  patch_string = time.strftime("{{Patch name|%m|%d|%Y}}", time.localtime(time.time() - (6*60*60))).replace('|0', '|'),
                                                  item_description = item.description if item.description else "",
                                                  min_level = item.min_level,
                                                  max_level = item.max_level,
                                                  level_type = item.type,
                                                  class_navs = class_navs
                                                  )
        elif item_type == 'weapon':
            template =   weapon_template().format(item_name = item.name.replace(' ', '_'),
                                                  proper_item_name = item.name,
                                                  class_links = class_links,
                                                  patch_string = time.strftime("{{Patch name|%m|%d|%Y}}", time.localtime(time.time() - (6*60*60))).replace('|0', '|'),
                                                  slot = item.slot_name,
                                                  item_description = item.description if item.description else "",
                                                  level = item.min_level,
                                                  level_type = item.type,
                                                  class_navs = class_navs
                                                  )
        elif item_type == 'action':
            pass

        if template:
            create_page(item.name, template)
            try:
                upload_backpack_image(item.name, item.image, item_type)
            except:
                pass

    # Save new current schema state
    save_current_schema_ids()

if __name__ == '__main__':
    print('Fetching list of new item ids...')
    new_ids = get_new_item_ids()

    if len(new_ids) == 0:
        print('No new item ids')
        sys.exit()

    print('{0} new items'.format(len(new_ids)))
    print('Creating pages...')

    generate_pages(new_ids)