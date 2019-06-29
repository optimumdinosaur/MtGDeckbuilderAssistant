import json

with open('AllCards.json', 'r', encoding='utf8') as cards_file:
	card_data = json.load(cards_file)
	trimmed_cards = {}
	for card in card_data:
		if card_data[card]["legalities"]:
			del card_data[card]['legalities']
			del card_data[card]['foreignData']
			if 'mtgstocksId' in card_data[card]:
				del card_data[card]['mtgstocksId']
			if 'prices' in card_data[card]:
				del card_data[card]['prices']
			del card_data[card]['printings']
			if 'purchaseUrls' in card_data[card]:
				del card_data[card]['purchaseUrls']
			if 'rulings' in card_data[card]:
				del card_data[card]['rulings']
			if 'scryfallOracleId' in card_data[card]:
				del card_data[card]['scryfallOracleId']
			if 'uuid' in card_data[card]:
				del card_data[card]['uuid']
			if 'supertypes' in card_data[card]:
				del card_data[card]['supertypes']
			if 'subtypes' in card_data[card]:
				del card_data[card]['subtypes']
			if 'types' in card_data[card]:
				del card_data[card]['types']
			if 'names' in card_data[card]:
				if not card_data[card]['names']:
					del card_data[card]['names']

			trimmed_cards[card] = card_data[card]
		
	with open ('TrimmedCards5.json', 'w') as output_file:
		json.dump(trimmed_cards, output_file)