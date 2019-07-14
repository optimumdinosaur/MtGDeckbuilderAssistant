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

	def CrunchNumbers(self):
		self.CalcCMCCurve()
		self.GetColorDistribution()
		self.GetTypeDistribution()
		self.GetCreatureSubtypes()

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
		print (f"Looking for card with name, {cardname}...")
		for card in self.mainboard:
			print (f"Checking card, {card.name}")
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

	def to_string(self):
		ret_val = f"Deck: {self.name}\n"
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


	def CalcCMCCurve(self):
		self.CMCCurve = []
		for card in self.mainboard:
			if "Land" not in card.type_line:
				if len(self.CMCCurve) < card.convertedManaCost+1:
					powerpole = [0] * (card.convertedManaCost - len(self.CMCCurve) + 1)
					self.CMCCurve.extend(powerpole)	
				self.CMCCurve[card.convertedManaCost] += self.mainboard[card]
		return self.CMCCurve

	def GetColorDistribution(self):
		self.color_dist = {'W': [0, 0], 'U': [0, 0], 'B': [0, 0], 'R': [0, 0], 'G': [0, 0], 'C':[0, 0]}
		for color in self.color_dist:
			for card in self.mainboard:
				if color in card.manaCost:
					self.color_dist[color][0] += self.mainboard[card]
					self.color_dist[color][1] += (card.manaCost.count(color) * self.mainboard[card])
		return self.color_dist

	def GetTypeDistribution(self):
		self.type_dist = {"Creature":0, "Enchantment":0, "Artifact":0, "Planeswalker":0, "Instant":0, "Sorcery":0, "Land":0}
		for t in self.type_dist:
			for c in self.mainboard:
				if t in c.type_line:
					self.type_dist[t] += self.mainboard[c]
		return self.type_dist

	def GetCreatureSubtypes(self):
		self.creature_subtypes = Counter()
		for card in self.mainboard:
			if "Creature" in card.type_line:
				card_subtypes = card.type_line[card.type_line.find('—'):].split()
				for subtype in card_subtypes:
					if '—' in subtype:
						continue
					self.creature_subtypes[subtype] += self.mainboard[card]
		return self.creature_subtypes

	# returns a list of Cards that conatain the re pattern
	def SearchByPhrase(self, pattern, cts = None):
		rv = []
		if cts is None:
			cts = self.mainboard
		for card in cts:
			ptrn = pattern.replace('{N}', card.name)
			if re.search(ptrn, card.text, re.I):
				rv.append(card)
		return rv

	def SearchByType(self, pattern, cts = None):
		rv = []
		if cts is None:
			cts = self.mainboard
		for card in cts:
			if pattern in card.type_line:
				rv.append(card)
		return rv

	# prints a list of Cards
	def PrintSearchResults(self, results):
		print ("Search Results:")
		for card in results:
			print (f"{self.mainboard[card]} - {str(card)}")