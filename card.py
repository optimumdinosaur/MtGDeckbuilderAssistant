import json
import MtGCardDBHandler

class Card:

	def __init__(self):
		self.name = ""
		self.cmc = 0
		self.mana_cost = ""
		self.colors = []
		self.color_id = set()
		self.type_line = ""
		self.text = ""

	def __init__(self, nm, database=None):
		if database is None:
			print ("Card.init: Loading database. !!! This is not the thing that should be loading the database !!!")
			# not sure why this is still an option honestly
			database = MtGCardDBHandler.LoadCardDataBase()
		try:
			card_data = database[nm]
		except KeyError:
			print (f"*** Card not found: {nm} ***")
			return
		self.name = nm
		self.colors = card_data['colors']
		if 'convertedManaCost' in card_data:
			self.cmc = int(card_data['convertedManaCost'])
		else:
			# some cards like Memnite have have a {0} manacost and for some reason no cmc property in db, so we'll check for that
			if 'manaCost' in card_data:
				print (f"{self.name} has no convertedManaCost but is a spell. Setting cmc to 0.")
				self.cmc = 0
			else:
				self.cmc = -1 # this way it still has a numerical value for sorting stuff
		if "names" in card_data:
			self.names = card_data["names"]
			self.layout = card_data["layout"]
			if nm == card_data["names"][0]:
				self.other_half = Card(self.names[1])
		try:
			self.mana_cost = card_data['manaCost']
		except KeyError:
			self.mana_cost = "{}"
		try:
			self.text = card_data['text']
		except KeyError:
			self.text = ""
		
		self.type_line = card_data['type']
		
		if "Creature" in self.type_line:
			self.power = card_data["power"]
			self.toughness = card_data["toughness"]
		else:
			self.power = None
			self.toughness = None
		
		if "loyalty" in card_data:
			self.loyalty = card_data["loyalty"]
		else:
			self.loyalty = None

		if 'multiverse_id' in card_data:
			self.multiverseId = card_data['multiverse_id']


		print ("Card created with name: " + nm)



	def __str__(self):
		ret_val = f"{self.name}: {self.mana_cost if 'Land' not in self.type_line else ''} {self.type_line} \n{self.text}"
		if "Creature" in self.type_line:
			ret_val += f" ({self.power}/{self.toughness})"
		if 'Planeswalker' in self.type_line:
			ret_val += f"\nLoyalty: {self.loyalty}"
		if hasattr(self, 'names'):
			if self.names[0] == self.name:
				ret_val += f"\n{self.layout.capitalize()}: {str(self.other_half)}"
		return ret_val

	def str_short(self):
		ret_val = f"{self.name} - {self.mana_cost}"
		return ret_val

	def __eq__(self, other):
		return (self.name == other.name)

	def __ne__(self, other):
		return (self.name != other.name)

	def __hash__(self):
		return hash(str(self))