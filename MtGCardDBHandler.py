import json

card_db_filepath = "TrimmedCards5.json"

def LoadCardDataBase(filepath = None):
	if filepath is None:
		filepath = card_db_filepath
	with open(filepath) as card_file:
		card_data = json.load(card_file)
	return card_data