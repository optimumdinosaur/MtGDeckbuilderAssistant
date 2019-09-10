import MtGCardDBHandler
from card import Card
import re
from collections import Counter


class Deck:

	def __init__(self, name = "", filepath=None, database=MtGCardDBHandler.LoadCardDataBase()):
		self.name = name
		self.mainboard = {}
		self.database = database
		if filepath:
			self.BuildFromFile(filepath)
		self.CrunchNumbers()

	def CrunchNumbers(self, dataset=None):
		if dataset is None:
			dataset = self.mainboard
		self.CountCards(dataset)
		self.CalcCMCCurve(dataset)
		self.GetColorDistribution(dataset)
		self.GetTotalDevotion(dataset)
		self.GetTypeDistribution(dataset)
		self.GetCreatureSubtypes(dataset)

	def AddCard(self, Card):
		try:
			self.mainboard[Card] += 1
		except KeyError:
			self.mainboard[Card] = 1

	def RemoveCard(self, Card):
		try:
			self.mainboard[Card] -= 1
			if self.mainboard[Card] <= 0:
				del self.mainboard[Card]
		except KeyError:
			print ("Card already not in deck.")

	def SetCardQuantity(self, cardname, qty):
		print (f"Setting card quantity for card, {cardname}, to {qty}...")
		for card in self.mainboard:
			# print (f"Checking card, {card.name}")
			if re.match(cardname, card.name, re.I):
				self.mainboard[card] = qty
				if qty <= 0:
					del self.mainboard[card]
				return

		if qty >= 1:
			c = Card(cardname, database=self.database)
			if hasattr(c, 'name'):
				self.mainboard[c] = qty
				print ("Card quantity set.")
			else:
				print ("Card quantity not set, name not found. ")

	def __str__(self):
		# ret_val = f"Deck: {self.name}\n"
		ret_val = ""
		for c in self.mainboard:
			ret_val += (f"{self.mainboard[c]} {c.name}\n")
		return ret_val

	def to_verbose_string(self):
		ret_val = f"Deck: {self.name}\n"
		for c in self.mainboard:
			ret_val += (f"{self.mainboard[c]} {str(c)}\n")
		return ret_val

	def BuildFromFile(self, filepath):
		self.name = filepath
		self.mainboard.clear()
		print ("Building a deck from file...")
		with open(filepath) as in_file:
			for line in in_file:
				print ("Looking at line: " + str(line))
				split_line = re.split("[x]?[ ]+", line, 1)
				card_name = split_line[1].strip()
				print ("Card name found to be : " + card_name)
				card = Card(card_name, self.database)
				self.mainboard[card] = int(split_line[0].strip())
				print ("card added to deck")

	def UpdateFromFile(self, filepath):
		with open(filepath) as in_file:
			for line in in_file:
				split_line = re.split("[x]?[ ]+", line, 1)
				card = Card(split_line[1].strip(), self.database)
				self.SetCardQuantity(card, int(split_line[0].strip()))

	def CountCards(self, dataset=None):
		if dataset is None:
			dataset = self.mainboard
		self.card_count = 0
		for card in dataset:
			self.card_count += self.mainboard[card]
		return self.card_count


	def CalcCMCCurve(self, dataset=None):
		if dataset is None:
			dataset=self.mainboard
		self.CMCCurve = []
		for card in dataset:
			if "Land" not in card.type_line:
				if len(self.CMCCurve) < card.cmc+1:
					powerpole = [0] * (card.cmc - len(self.CMCCurve) + 1)
					self.CMCCurve.extend(powerpole)	
				self.CMCCurve[card.cmc] += self.mainboard[card]
		return self.CMCCurve


	# creates and returns a dictionary containing data on the colors in the deck
	# keys are each color, as well as Colorless
	# the values are a 2 element list. 
	# the first element is the number of cards of that color
	# the second is the deck's total devotion to that color (how many times that mana symbol appears in the cost of each of card of the deck)
	def GetColorDistribution(self, dataset=None):
		if dataset is None:
			dataset = self.mainboard
		self.color_dist = {'W': [0, 0], 'U': [0, 0], 'B': [0, 0], 'R': [0, 0], 'G': [0, 0], 'C':[0, 0]}
		for color in self.color_dist:
			for card in dataset:
				if color in card.mana_cost:
					self.color_dist[color][0] += self.mainboard[card]
					self.color_dist[color][1] += (card.mana_cost.count(color) * self.mainboard[card])
		return self.color_dist

	def GetTotalDevotion(self, dataset=None):
		if dataset is None:
			dataset = self.mainboard
		self.total_devotion = 0
		colors = ['W', 'U', 'B', 'R', 'G', 'C']
		for card in dataset:
			for c in colors:
				self.total_devotion += card.mana_cost.count(c) * self.mainboard[card]
		print (f"Total Devotion to all colors: {self.total_devotion}")
		return self.total_devotion

	def GetTypeDistribution(self, dataset=None):
		if dataset is None:
			dataset = self.mainboard
		self.type_dist = {"Creature":0, "Enchantment":0, "Artifact":0, "Planeswalker":0, "Instant":0, "Sorcery":0, "Land":0}
		for t in self.type_dist:
			for c in dataset:
				if t in c.type_line:
					self.type_dist[t] += self.mainboard[c]
		return self.type_dist

	def GetCreatureSubtypes(self, dataset=None):
		if dataset is None:
			dataset = self.mainboard
		self.creature_subtypes = Counter()
		for card in dataset:
			if "Creature" in card.type_line:
				card_subtypes = card.type_line[card.type_line.find('—'):].split()
				for subtype in card_subtypes:
					if '—' in subtype:
						continue
					self.creature_subtypes[subtype] += self.mainboard[card]
		return self.creature_subtypes


	# searches by comparing integer values on each card like power, toughness, cmc
	# cproperty : which card property is being compared, represented by a single character P, T, or C
	# value : what the search compares the value on card to
	# comparison : how the search compares those values
	def SearchByValueComparison(self, cproperty, value, comparison, dataset = None):
		if dataset is None:
			dataset = self.mainboard
		def EqualTo(card_value, comp_value):
			return (card_value == comp_value)
		def LessThan(card_value, comp_value):
			return (card_value < comp_value)
		def GreaterThan(card_value, comp_value):
			return (card_value > comp_value)
		def LessEqual(card_value, comp_value):
			return (card_value <= comp_value)
		def GreaterEqual(card_value, comp_value):
			return (card_value >= comp_value)
		comp_switcher = { '=' : EqualTo, '<' : LessThan, '>' : GreaterThan, '<=' : LessEqual, '>=' : GreaterEqual }
		func = comp_switcher.get(comparison)
		rv = []

		for card in dataset:
			property_switcher = {'P' : card.power, 'T' : card.toughness, 'C' : card.cmc}
			card_value = property_switcher.get(cproperty)
			if card_value is None:
				continue
			if func(int(card_value), int(value)):
				rv.append(card)
		return rv

	def SearchByName(self, pattern, dataset = None):
		if dataset is None:
			dataset = self.mainboard
		rv = []
		for card in dataset:
			if re.search(pattern, card.name, re.I):
				rv.append(card)
		return rv

	# returns a list of Cards that conatain the re pattern
	def SearchByPhrase(self, pattern, dataset = None):
		if dataset is None:
			dataset = self.mainboard
		rv = []
		for card in dataset:
			ptrn = pattern.replace('{N}', card.name)
			if re.search(ptrn, card.text, re.I):
				rv.append(card)
		return rv

	def SearchByType(self, pattern, dataset = None):
		rv = []
		if dataset is None:
			dataset = self.mainboard
		for card in dataset:
			if re.search(pattern, card.type_line, re.I):
				rv.append(card)
		return rv


	def SearchByColor(self, pattern, dataset = None):
		rv = []
		if dataset is None:
			dataset = self.mainboard
		for card in dataset:
			if pattern in card.mana_cost:
				rv.append(card)
		return rv

	# prints a list of Cards
	def PrintSearchResults(self, results):
		print ("Search Results:")
		for card in results:
			print (f"{self.mainboard[card]} - {str(card)}")