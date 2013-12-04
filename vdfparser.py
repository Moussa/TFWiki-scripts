# A class for parsing TF2 vdf files.
# The hard work was done by WindPower,
# I just wrote the methods :)

import re
import steam

class VDF:
	def __init__(self, loc='tf_english.txt'):
		""" Initialize the class by reading in items_game.txt
		    and the localization file, if needed.
			
			Set loc to None to avoid reading a localization
			file.
		"""
		self.vdfstring = open('items_game.txt', 'rb').read()
		self.vdfstring = self.vdfstring.decode('utf-8')
		if loc is not None:
			self.locfile = open(loc, 'rb').read()
			try:
				self.locfile = self.locfile.decode('utf-16')
			except:
				# Already decoded
				pass

		self.finalParsed = steam.vdf.loads(self.vdfstring)

	def get_localized_item_name(self, itemnametoken):
		""" Returns the localized item name of any
			item, given the token name.
		"""
		tfenglishRE = re.compile(r'"%s"[\s\t]*"(.[^"]+)"' % itemnametoken[1:], re.IGNORECASE)
		res = tfenglishRE.search(self.locfile)
		if res:
			return res.group(1)
		else:
			return None

	def get_items(self):
		""" Returns the entire items dict. """
		return self.finalParsed['items_game']['items']

	def get_prefabs(self):
		""" Returns the entire prefabs dict. """
		return self.finalParsed['items_game']['prefabs']

	def get_item(self, key, value, allmatches=False):
		""" Returns the item dict that matches the
			given key and value.
			
			If allmatches is set to True, return all items
			that match the given key and value.
		"""
		items = []
		for item in self.finalParsed['items_game']['items']:
			if key in self.finalParsed['items_game']['items'][item]:
				keyval = self.finalParsed['items_game']['items'][item][key]
				if keyval == value:
					if allmatches:
						items.append(self.finalParsed['items_game']['items'][item])
					else:
						return self.finalParsed['items_game']['items'][item]
		return items