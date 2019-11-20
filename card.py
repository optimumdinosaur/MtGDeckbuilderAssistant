import json
import MtGCardDBHandler

class Card:

	def __init__(self):
		self.name = ""
		self.cmc = 0
		self.mana_cost = ""
		self.colors = []
		self.type_line = ""
		self.text = ""

	def __init__(self, nm, database=None):
		if database is None:
			print ("Card.init: Loading database. This is not the thing that should be loading database.")
			database = MtGCardDBHandler.LoadCardDataBase()
		print (f"nm - {nm}")
		try:
			card_data = database[nm]
		except KeyError:
			print (f"*** Card not found: {nm} ***")
			return
		self.name = nm
		self.colors = card_data['colors']
		self.cmc = int(card_data['convertedManaCost'])
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
		print ("Card created with name: " + nm)

	def __str__(self):
		ret_val = f"{self.name}: {self.mana_cost} {self.type_line} - {self.text}"
		if "Creature" in self.type_line:
			ret_val += f" ({self.power}/{self.toughness})"
		if 'Planeswalker' in self.type_line:
			ret_val += f"\nLoyalty: {self.loyalty}"
		if hasattr(self, 'names'):
			if self.names[0] == self.name:
				ret_val += f"\n{self.layout.capitalize()}: {str(self.other_half)}"
		return ret_val