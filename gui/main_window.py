import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from core.player import Player  # Add this line
from core.game_engine import MonopolyTracker

class MonopolyGUI:
    def __init__(self, root):
        self.root = root
        self.tracker = MonopolyTracker()
        self.create_widgets()
        self.update_player_list()

    def create_widgets(self):
        # Player List Frame
        self.player_frame = ttk.LabelFrame(self.root, text="Players")
        self.player_frame.pack(pady=10, padx=10, fill=tk.BOTH)
        
        self.player_list = tk.Listbox(self.player_frame, height=8)
        self.player_list.pack(fill=tk.BOTH, expand=True)
        self.player_list.bind('<<ListboxSelect>>', self.show_player_details)
        
        # Action Buttons
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=5)
        
        ttk.Button(btn_frame, text="Add Player", command=self.add_player).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Update Money", command=self.update_money).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Add Property", command=self.add_property).grid(row=0, column=2, padx=5)
        ttk.Button(btn_frame, text="Move Player", command=self.move_player).grid(row=0, column=3, padx=5)
        ttk.Button(btn_frame, text="Toggle Jail", command=self.toggle_jail).grid(row=0, column=4, padx=5)
        
        # Details Panel
        self.details_frame = ttk.LabelFrame(self.root, text="Player Details")
        self.details_frame.pack(pady=10, padx=10, fill=tk.BOTH)
        
        self.details_text = tk.Text(self.details_frame, height=10)
        self.details_text.pack(fill=tk.BOTH, expand=True)
        
        # Save/Load Buttons
        ttk.Button(self.root, text="Save Game", command=self.tracker.save_game).pack(side=tk.LEFT, padx=10)
        ttk.Button(self.root, text="Load Game", command=self.load_game).pack(side=tk.RIGHT, padx=10)

    # ... (Keep all other MonopolyGUI methods unchanged from previous version)
    # [Include all remaining methods like update_player_list, add_player, etc.]
    
    def update_player_list(self):
        self.player_list.delete(0, tk.END)
        for player in self.tracker.players:
            self.player_list.insert(tk.END, player.name)

    def show_player_details(self, event=None):
        selection = self.player_list.curselection()
        if not selection:
            return
        
        player = self.tracker.players[selection[0]]
        details = (
            f"Name: {player.name}\n"
            f"Money: ${player.money}\n"
            f"Properties: {', '.join(player.properties) or 'None'}\n"
            f"Position: {player.position}\n"
            f"Jail Status: {'In Jail' if player.in_jail else 'Free'}"
        )
        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(tk.END, details)

    def add_player(self):
        name = simpledialog.askstring("Add Player", "Enter player name:")
        if name:
            if any(p.name.lower() == name.lower() for p in self.tracker.players):
                messagebox.showerror("Error", "Player already exists!")
            else:
                from core.player import Player  # Explicit import
                new_player = Player(name)
                self.tracker.players.append(new_player)
                self.update_player_list()

    def get_selected_player(self):
        selection = self.player_list.curselection()
        if not selection:
            messagebox.showwarning("Warning", "No player selected!")
            return None
        return self.tracker.players[selection[0]]

    def update_money(self):
        player = self.get_selected_player()
        if not player:
            return
        
        amount = simpledialog.askinteger("Update Money", "Enter amount (+/-):", parent=self.root)
        if amount:
            player.money += amount
            self.show_player_details()

    def add_property(self):
        player = self.get_selected_player()
        if not player:
            return
        
        prop = simpledialog.askstring("Add Property", "Enter property name:")
        if prop:
            player.properties.append(prop)
            self.show_player_details()

    def move_player(self):
        player = self.get_selected_player()
        if not player:
            return
        
        spaces = simpledialog.askinteger("Move Player", "Enter spaces to move:", parent=self.root)
        if spaces:
            player.position = (player.position + spaces) % 40
            self.show_player_details()

    def toggle_jail(self):
        player = self.get_selected_player()
        if player:
            player.in_jail = not player.in_jail
            self.show_player_details()

    def load_game(self):
        if self.tracker.load_game():
            self.update_player_list()