from .player import Player
import json
import os
from tkinter import messagebox

class MonopolyTracker:
    def __init__(self):
        self.players = []
        self.save_file = "data/saved_games/latest.json"
        self.transaction_log = []

    def save_game(self):
        try:
            os.makedirs(os.path.dirname(self.save_file), exist_ok=True)
            data = [p.to_dict() for p in self.players]
            with open(self.save_file, 'w') as f:
                json.dump(data, f)
            messagebox.showinfo("Success", "Game saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Save failed: {str(e)}")

    def load_game(self):
        try:
            if os.path.exists(self.save_file):
                with open(self.save_file, 'r') as f:
                    data = json.load(f)
                self.players = [Player.from_dict(p) for p in data]
                messagebox.showinfo("Success", "Game loaded!")
                return True
            messagebox.showwarning("Warning", "No save file found")
            return False
        except Exception as e:
            messagebox.showerror("Error", f"Load failed: {str(e)}")
            return False