"""
Handles loading the card database JSON file
The sole function, LoadCardDataBase, loads a JSON file containing a database of Magic: the Gathering cards
Returns a dictionary containing all the data in the file
"""


import json

card_db_filepath = "Doublechecked MtgDB from SDK.json"
def LoadCardDataBase(filepath = None):
	if filepath is None:
		filepath = card_db_filepath
	with open(filepath) as card_file:
		card_data = json.load(card_file)
	print (f"Card database retrieved from {card_db_filepath}.")
	return card_data

print ("DB Handler loaded.")