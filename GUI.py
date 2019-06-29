import MtGCardDBHandler
from card import Card
from deck import Deck
from tooltip import CreateToolTip
import tkinter as tk

class Manager (tk.Frame):
	def __init__(self, master=None, deck = None):
		super().__init__(master)
		self.master = master
		if deck:
			self.LoadDeck(deck)
			self.ShowDeckList()
			self.ShowCMCGraph()
		self.pack()

	def LoadDeck(self, d):
		self.deck = d

	def ShowDeckList(self):
		decklist_frame = tk.LabelFrame(self, text="DeckList", padx=5, pady=5)
		decklist_frame.pack(side="left")
		artifact_frame = tk.LabelFrame(decklist_frame, text="Artifacts", padx=2, pady=2)
		creature_frame = tk.LabelFrame(decklist_frame, text="Creatures", padx=2, pady=2)
		ench_frame = tk.LabelFrame(decklist_frame, text="Enchantments", padx=2, pady=2)
		pw_frame = tk.LabelFrame(decklist_frame, text="Planeswalkers", padx=2, pady=2)
		instant_frame = tk.LabelFrame(decklist_frame, text="Instants", padx=2, pady=2)
		sorcery_frame = tk.LabelFrame(decklist_frame, text="Sorceries", padx=2, pady=2)
		land_frame = tk.LabelFrame(decklist_frame, text="Lands", padx=2, pady=2)
		for card in self.deck.mainboard:
			if "Artifact" in card.type_line:
				mstr = artifact_frame
			if "Enchantment" in card.type_line:
				mstr = ench_frame
			if "Instant" in card.type_line:
				mstr = instant_frame
			if "Sorcery" in card.type_line:
				mstr = sorcery_frame
			if "Planeswalker" in card.type_line:
				mstr = pw_frame
			if "Creature" in card.type_line:
				mstr = creature_frame
			if "Land" in card.type_line:
				mstr = land_frame

			card_frame = tk.Frame(master = mstr)
			card_label = tk.Label(master = card_frame, text=f"{card.name} - {card.manaCost}")
			qty_label = tk.Label(master = card_frame, text=self.deck.mainboard[card])
			card_label.grid(row=0, column=1)
			card_ttp = CreateToolTip(card_label, str(card))
			qty_label.grid(row=0, column=0)
			card_frame.pack(anchor="w")

		creature_frame.pack(anchor="w")
		artifact_frame.pack(anchor="w")
		ench_frame.pack(anchor="w")
		pw_frame.pack(anchor="w")
		instant_frame.pack(anchor="w")
		sorcery_frame.pack(anchor="w")
		land_frame.pack(anchor="w")

	def ShowCMCGraph(self):
		cmc_frame = tk.LabelFrame(self, text="Converted Mana Costs", padx=5, pady=5)
		cmc_frame.pack(side="right", anchor="n")
		c_width = 300
		c_height = 200
		cmc_canvas = tk.Canvas(cmc_frame, width = c_width, height = c_height)
		cmc_canvas.pack()
		y_stretch = 10
		y_gap = 5
		x_stretch = 10
		x_width = 16
		x_gap = 8
		for x, y in enumerate(self.deck.CMCCurve):
			x0 = x * x_stretch + x * x_width + x_gap
			y0 = c_height - (y * y_stretch + y_gap)
			x1 = x0 + x_width
			y1 = c_height - y_gap
			cmc_canvas.create_rectangle(x0, y0, x1, y1, fill="orange")
			cmc_canvas.create_text(x0+2, y0, anchor=tk.SW, text=str(y))




db = MtGCardDBHandler.LoadCardDataBase()
file_deck = Deck(filepath='rw-manabarbs.txt')
r = tk.Tk()
r.title("MtG DeckBuilding Assistant")
manager = Manager(master = r, deck = file_deck)
r.mainloop()