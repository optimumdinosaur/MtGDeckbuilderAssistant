# MtGDeckbuilderAssistant
Python application to help with building decks in Magic: the Gathering


Work in progress.
Displays decklist, CMC graph, as well as type and color distribution for a deck. Set the number of a card in a deck with the entry box and spinbox at the bottom. This works to add new cards, remove cards, or just adjust quantities. Decklist, graphs, and distributions all update when you change a card quantity. 
There is now a Search box that searches the rules text of each card using regular expressions for the pattern. You can also subtitute {N} for the card's name in your search pattern. For example you can use the pattern, "{N} deals [\d]+ damage", to find all cards that deal any amount of fixed damage. 
There's also checkboxes to filter cards by Type or Color. The Search and Filter will update the list of cards displayed and all its graphs, type distribution numbers, etc, but will not change the Deck's actual decklist.
Decks can be saved to and loaded from files. The loaded file needs to have one line per card with the card quantity first, then the card name. For example, "4 Lightning Bolt"
