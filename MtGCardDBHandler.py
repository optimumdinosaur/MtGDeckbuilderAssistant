import json

card_db_filepath = "AllCards.json"
def LoadCardDataBase(filepath = None):
	if filepath is None:
		filepath = card_db_filepath
	with open(filepath) as card_file:
		card_data = json.load(card_file)
	print ("Card database retrieved.")
	return card_data

print ("DB Handler loaded.")