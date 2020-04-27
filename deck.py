import MtGCardDBHandler
from card import Card
import re
from collections import Counter


class Deck:

	def __init__(self, name = "", filepath=None, database=None):
		self.name = name
		self.mainboard = {}
		self.image_dict = {}
		if database is None:
			print ("Deck.init: Loading database...")
			database = MtGCardDBHandler.LoadCardDataBase()
		self.database = database
		if filepath:
			self.BuildFromFile(filepath)
		print ("Deck.init: about to CrunchNumbers")
		self.CrunchNumbers()
		self.MakeDefaultSorts()

	def CrunchNumbers(self, dataset=None):
		if dataset is None:
			dataset = self.mainboard
		self.CountCards(dataset)
		self.CalcCMCCurve(dataset)
		self.GetColorDistribution(dataset)
		self.GetTypeDistribution(dataset)
		self.GetCreatureSubtypes(dataset)

	def MakeDefaultSorts(self):
		self.sorts = { "Type" : {}, "Color" : {}, "Converted Mana Cost" : {} }
		for card in self.mainboard:
			# Sort for Type
			self.SortCardByType(card)
			# Sort for Color
			self.SortCardByColors(card)
			# Sort for Converted Mana Cost
			self.SortCardByCMC(card)

	def SortCardByType(self, card):
		type_list = ['Creature', 'Artifact', 'Enchantment', 'Planeswalker', 'Instant', 'Sorcery', 'Land']
		# look for Creature first so Artifact Creatures, Enchantment Creatures, and Land Creatures get sorted in there
		for t in type_list:
			if t in card.type_line:
				if t not in self.sorts['Type']:
					self.sorts['Type'][t] = Category(t)
				self.sorts['Type'][t].add(card)
				return # we're done here, no need to check other types

	def SortCardByColors(self, card):
		colors = set(card.colors)
		if hasattr(card, 'other_half'): # if card has two spells on it
			colors |= set(card.other_half.colors) # include the other half's colors

		if len(colors) > 1: # if multicolor
			if 'Multi' not in self.sorts['Color']:
				self.sorts['Color']['Multi'] = Category('Multicolor')
			self.sorts['Color']['Multi'].add(card)
		elif len(colors) == 0: # if colorless
			if 'Colorless' not in self.sorts['Color']:
				self.sorts['Color']['Colorless'] = Category('Colorless')
			self.sorts['Color']['Colorless'].add(card)
		else: # the card is one color
			color_list = ['White', 'Blue', 'Black', 'Red', 'Green']
			for c in color_list: 
				if c in colors: # if card is this Color
					if c not in self.sorts['Color']: # if there's not already a Category for this Color
						self.sorts['Color'][c] = Category(c) # create a Category for this Color
					self.sorts['Color'][c].add(card) # add the Card to the Category for this Color
					return # we're done here, no need to check other colors

	def SortCardByCMC(self, card):
		print (f"Deck.SortCardByCMC: looking at {card.name}")
		cat_name = "Land / Nonspells" if card.cmc == -1 else str(card.cmc)
		print (f"Deck.SortCardByCMC: {card.name}'s cat_name: {cat_name}")
		if cat_name not in self.sorts['Converted Mana Cost']:
			self.sorts['Converted Mana Cost'][cat_name] = Category(cat_name)
			print (f"Deck.SortCardByCMC: Created new Category for {cat_name}")
		
		self.sorts['Converted Mana Cost'][cat_name].add(card)
		print (f"Deck.SortCardByCMC: {card.name} added to {cat_name} Category")


	def SetCardQuantity(self, cardname, qty):
		print (f"Setting card quantity for card, {cardname}, to {qty}...")
		card = Card(cardname, database=self.database)
		# if card is in deck already
		if card in self.mainboard:
			if qty <= 0:
				print (f"Removing {card.name} from mainboard...")
				# remove the card from mainboard
				del self.mainboard[card]
				print (f"Card removed from mainboard!")
				# remove card from sorts
				print (f"Removing {card.name} from sorts...")
				for sort in self.sorts:
					for category in self.sorts[sort]:
						if card in self.sorts[sort][category].cards:
							self.sorts[sort][category].remove(card)
							print (f"Deck.SetCardQuantity: {card.name} removed from {category} in {sort}")

						# try:
						# 	del sort[category][card]
						# 	print (f"Deck.SetCardQuantity: {card.name} removed from {category} in {sort}")
						# 	break # out of this particular sort's loop; it won't be in another category
						# except:
						# 	pass # not in this category, moving on
			else: # qty is above 0
				self.mainboard[card] = qty
				print (f"Deck.SetCardQuantity: {card.name} quantity set to {self.mainboard[card]}")
				# since it's already in the Deck it should be sorted
		else: # card is not already in deck
			if qty <= 0:
				print (f"Deck.SetCardQuantity: {card.name} already not in deck. No need to set its quantity to {qty}")
			else: # qty is above 0
				self.mainboard[card] = qty
				# sort the card, just the default sorts for now: Type and Colors
				self.SortCardByType(card)
				self.SortCardByColors(card)
				self.SortCardByCMC(card)



	def __str__(self):
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
			self.card_count += int(self.mainboard[card])
		return self.card_count


	def CalcCMCCurve(self, dataset=None):
		if dataset is None:
			dataset=self.mainboard
		self.CMCCurve = []
		for card in dataset:
			if "Land" not in card.type_line:
				if not hasattr(card, 'cmc'):
					card.cmc = 0
				if len(self.CMCCurve) < card.cmc+1:
					powerpole = [0] * (card.cmc - len(self.CMCCurve) + 1)
					self.CMCCurve.extend(powerpole)	
				self.CMCCurve[card.cmc] += self.mainboard[card]
		return self.CMCCurve


	# creates and returns a dictionary, self.color_dist, containing data on the colors in the deck
	# keys are each color, as well as Colorless
	# the values are each a 3 element list 
	# the first element is the number of cards of that color
	# the second is the deck's total devotion to that color (how many times that mana symbol appears in the cost of each of card of the deck)
	# the third is the number of lands that provide this color mana
	def GetColorDistribution(self, dataset=None):
		if dataset is None:
			dataset = self.mainboard
		self.color_dist = {'W': [0, 0, 0], 'U': [0, 0, 0], 'B': [0, 0, 0], 'R': [0, 0, 0], 'G': [0, 0, 0], 'C':[0, 0, 0]}
		self.total_devotion = 0
		self.total_land_devotion = 0 
		for color in self.color_dist:
			for card in dataset:
				if color in card.mana_cost:
					self.color_dist[color][0] += self.mainboard[card]
					devotion_from_card = card.mana_cost.count(color) * self.mainboard[card]
					self.color_dist[color][1] += devotion_from_card
					self.total_devotion += devotion_from_card

				if 'Land' in card.type_line:
					pattern = ':.*{'+color+'}.*$'
					if re.search(pattern, card.text, re.M):
						self.color_dist[color][2] += self.mainboard[card]
						self.total_land_devotion += self.mainboard[card]					
		return self.color_dist

	# creates and returns a dictionary, self.type_dist containing a count of each Type of card in the deck
	# keys are each Type
	# each value is the number of cards of that Type
	# cards with multiple types add to the count for each of their types
	def GetTypeDistribution(self, dataset=None):
		if dataset is None:
			dataset = self.mainboard
		self.type_dist = {"Creature":0, "Enchantment":0, "Artifact":0, "Planeswalker":0, "Instant":0, "Sorcery":0, "Land":0}
		for t in self.type_dist:
			for c in dataset:
				if t in c.type_line:
					self.type_dist[t] += self.mainboard[c]
		return self.type_dist

	# creates and returns a Counter, self.creature_subtypes, containing the number of cards of each creature subtype in the deck
	# keys are each creature subtype
	# each value is the number of cards with that subtype
	def GetCreatureSubtypes(self, dataset=None):
		if dataset is None:
			dataset = self.mainboard
		self.creature_subtypes = Counter()
		for card in dataset:
			if "Creature" in card.type_line or "Tribal" in card.type_line:
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
		comp_switcher = { '=' : EqualTo, 
						  '<' : LessThan, 
						  '>' : GreaterThan, 
						  '<=' : LessEqual, 
						  '>=' : GreaterEqual, 
						 }
		func = comp_switcher.get(comparison)
		rv = []

		for card in dataset:
			property_switcher = {'P' : card.power, 
								 'T' : card.toughness, 
								 'C' : card.cmc,
								 }
			card_value = property_switcher.get(cproperty)
			if card_value is None:
				continue
			if func(int(card_value), int(value)):
				rv.append(card)
		return rv

	# returns a list of Cards with the pattern in their name
	def SearchByName(self, pattern, dataset = None):
		if dataset is None:
			dataset = self.mainboard
		rv = []
		for card in dataset:
			if re.search(rf'{pattern}', card.name, re.I):
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

	# Searches the card.type_line by whole word
	# Used for searching Type and Subtype
	def SearchByType(self, pattern, dataset = None):
		rv = []
		if dataset is None:
			dataset = self.mainboard
		for card in dataset:
			if re.search(rf'\b{pattern}\b', card.type_line, re.I):
				rv.append(card)
		return rv

	# returns a list of Cards with the pattern Color in their mana cost
	def SearchByColor(self, pattern, dataset = None):
		rv = []
		if dataset is None:
			dataset = self.mainboard
		for card in dataset:
			if pattern in card.mana_cost:
				rv.append(card)
		return rv


# stores a group of cards to be put together into a sort
class Category:
	def __init__(self, name=""):
		self.name = name
		self.cards = set()

	def __len__(self):
		return len(self.cards)
	
	def add(self, card):
		self.cards.add(card)

	def remove(self, card):
		self.cards.remove(card)

	def __str__(self):
		return f"{self.name}: {str(self.cards)}"

	def __hash__(self):
		return hash(str(self))

	# these should really be look at the cards too but I'll worry about that later
	def __eq__(self, other):
		return (self.name == other.name)

	def __ne__(self, other):
		return (self.name != other.name)