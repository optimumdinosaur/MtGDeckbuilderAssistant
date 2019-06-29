import MtGCardDBHandler
from card import Card
import re


class Deck:

	def __init__(self, name = "", filepath=None):
		self.name = name
		self.mainboard = {}
		if filepath:
			self.BuildFromFile(filepath)
			self.CalcCMCCurve()

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

	def SetCardQuantity(self, card, qty):
		self.mainboard[card] = qty
		if qty <= 0 and card in self.mainboard:
			del self.mainboard[card]

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

	def BuildFromFile(self, filepath, db=MtGCardDBHandler.LoadCardDataBase()):
		self.name = filepath
		self.mainboard.clear()
		with open(filepath) as in_file:
			for line in in_file:
				split_line = re.split("[x]?[ ]+", line, 1)
				card = Card(split_line[1].strip(), db)
				self.SetCardQuantity(card, int(split_line[0].strip()))

	def UpdateFromFile(self, filepath, db=MtGCardDBHandler.LoadCardDataBase()):
		with open(filepath) as in_file:
			for line in in_file:
				split_line = re.split("[x]?[ ]+", line, 1)
				card = Card(split_line[1].strip(), db)
				self.SetCardQuantity(card, int(split_line[0].strip()))


	def CalcCMCCurve(self):
		self.CMCCurve = []
		for card in self.mainboard:
			if "Land" not in card.type_line:
				if len(self.CMCCurve) < card.convertedManaCost+1:
					powerpole = [0] * (card.convertedManaCost - len(self.CMCCurve) + 1)
					self.CMCCurve.extend(powerpole)	
				self.CMCCurve[card.convertedManaCost] += self.mainboard[card]


	# returns a list of Cards that conatain the re pattern
	def SearchByPhrase(self, pattern, ctc = None):
		rv = []
		if ctc is None:
			ctc = self.mainboard
		for card in ctc:
			ptrn = pattern.replace('{N}', card.name)
			if re.search(ptrn, card.text, re.I):
				rv.append(card)
		return rv

	def SearchByType(self, pattern, ctc = None):
		rv = []
		if ctc is None:
			ctc = self.mainboard
		for card in ctc:
			if pattern in card.type_line:
				rv.append(card)
		return rv

	# prints a list of Cards
	def PrintSearchResults(self, results):
		print ("Search Results:")
		for card in results:
			print (f"{self.mainboard[card]} - {str(card)}")



# db = MtGCardDBHandler.LoadCardDataBase()
# filedeck = Deck()
# filepath = "rw-manabarbs.txt"
# # filepath = "grixis-zombies-w-burning-vengeance.txt"
# filedeck.BuildFromFile(filepath, db)
# print (filedeck.to_string())
# filedeck.CalcCMCCurve()
# print (filedeck.CMCCurve)

# pattern = "{N} deals [\d]+ damage"
# print ("Searching for " + pattern + "...")
# firstresults = filedeck.SearchByPhrase(pattern)
# filedeck.PrintSearchResults(firstresults)
# second_pattern = "it deals [\d]+ damage"
# print ("Also searching for " + second_pattern + "...")
# second_results = filedeck.SearchByPhrase(second_pattern)
# filedeck.PrintSearchResults(second_results)

# ttsf = "Enchantment"
# print ("\nNarrowing search down to " + ttsf +"s...")
# filedeck.PrintSearchResults( filedeck.SearchByType(ttsf, firstresults))