import json
import MtGCardDBHandler

class Card:

	def __init__(self):
		self.name = ""
		self.convertedManaCost = 0
		self.manaCost = ""
		self.colors = []
		self.type_line = ""
		self.text = ""

	def __init__(self, nm, data_base=None):
		self.name = nm
		if data_base is None:
			data_base = MtGCardDBHandler.LoadCardDataBase()
		try:
			card_data = data_base[nm]
		except KeyError:
			print (f"Card not found: {nm}")
			return
		self.colors = card_data['colors']
		self.convertedManaCost = int(card_data['convertedManaCost'])
		if "names" in card_data:
			self.names = card_data["names"]
			self.layout = card_data["layout"]
			if nm == card_data["names"][0]:
				self.other_half = Card(self.names[1])
		try:
			self.manaCost = card_data['manaCost']
		except KeyError:
			self.manaCost = "{}"
		try:
			self.text = card_data['text']
		except KeyError:
			self.text = ""
		self.type_line = card_data['type']
		if "Creature" in self.type_line:
			self.power = card_data["power"]
			self.toughness = card_data["toughness"]
		if "loyalty" in card_data:
			self.loyalty = card_data["loyalty"]

	def __str__(self):
		ret_val = f"{self.name}: {self.manaCost} {self.type_line} - {self.text}"
		if "Creature" in self.type_line:
			ret_val += f" ({self.power}/{self.toughness})"
		if hasattr(self, 'loyalty'):
			ret_val += f"\nLoyalty: {self.loyalty}"
		if hasattr(self, 'names'):
			if self.names[0] == self.name:
				ret_val += f"\n{self.layout.capitalize()}: {self.other_half.to_string()}"
		return ret_val