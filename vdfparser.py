# A class for parsing TF2 vdf files.
# The hard work was done by WindPower,
# I just wrote the methods :)

import re

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
			self.locfile = self.locfile.decode('utf-16')

		rString = re.compile(r'"([^"]+)"[ \t]*"([^"]*)"')
		rDictionary = re.compile(r'"([^"]+)"\s*\{([^"{}]+)\}')
		rValues = re.compile(r'~OHAI~(\d+)~')

		self.valueCount = -1
		self.values = []
		def registerString(m):
			self.valueCount += 1
			self.values.append((m.group(1), m.group(2)))
			return '~OHAI~' + str(self.valueCount) + '~'

		self.vdfstring = rString.sub(registerString, self.vdfstring)

		d = {}
		while True:
			m = rDictionary.search(self.vdfstring)
			if m is None:
				break
			d = {}
			for v in rValues.finditer(m.group(2)):
				val = self.values[int(v.group(1))]
				d[val[0]] = val[1]
			self.valueCount += 1
			self.values.append((m.group(1), d))
			self.vdfstring = self.vdfstring[:m.start()] + '~OHAI~' + str(self.valueCount) + '~' + self.vdfstring[m.end():]

		self.finalParsed = self.values[-1]

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
		return self.finalParsed[1]['items']

	def get_prefabs(self):
		""" Returns the entire prefabs dict. """
		return self.finalParsed[1]['prefabs']

	def get_item(self, key, value, allmatches=False):
		""" Returns the item dict that matches the
			given key and value.
			
			If allmatches is set to True, return all items
			that match the given key and value.
		"""
		items = []
		for item in self.finalParsed[1]['items']:
			if key in self.finalParsed[1]['items'][item]:
				keyval = self.finalParsed[1]['items'][item][key]
				if keyval == value:
					if allmatches:
						items.append(self.finalParsed[1]['items'][item])
					else:
						return self.finalParsed[1]['items'][item]
		return items