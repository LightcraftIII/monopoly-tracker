import json
import os
from tkinter import messagebox
from datetime import datetime
from core.player import Player  # Ensure correct import
from core.property import Property

class MonopolyTracker:
    def __init__(self):
        self.players = []
        self.properties = self.load_france_properties()
        self.transaction_log = []  # Initialize the log
        self.save_file = "data/saved_games/latest.json"
        
        # Log property creation
        for prop in self.properties:
            self.transaction_log.append({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "player": "Bank",
                "amount": prop.price,
                "reason": f"Created {prop.name}"
            })
        
    def load_france_properties(self):
        prop_file = os.path.join(os.path.dirname(__file__), "..", "data", "france_properties.json")
        with open(prop_file) as f:
            data = json.load(f)
        return [Property(**p) for p in data]
        
    def log_transaction(self, player, amount, reason):
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "player": player.name,
            "amount": amount,
            "new_balance": player.money,
            "reason": reason
        }
        self.transaction_log.append(entry)
        print(entry)  # Add this line to print the log entry
        
    def charge_rent(self, payer, property):
        if not property.owner or property.owner == payer:
            return
        
        rent = property.calculate_rent()
        if payer.money >= rent:
            payer.money -= rent
            property.owner.money += rent
            self.log_transaction(payer, -rent, f"Paid rent for {property.name}")
            self.log_transaction(property.owner, rent, f"Received rent for {property.name}")
        else:
            self.handle_bankruptcy(payer, property.owner, rent)

    def save_game(self):
        try:
            data = {
                "players": [p.to_dict() for p in self.players],
                "properties": [p.to_dict() for p in self.properties],
                "transactions": self.transaction_log
            }
            with open(self.save_file, 'w') as f:
                json.dump(data, f, default=str)  # Ensure all objects are serializable
            messagebox.showinfo("Success", "Game saved!")
        except Exception as e:
            messagebox.showerror("Error", f"Save failed: {str(e)}")

    def load_game(self):
        try:
            if os.path.exists(self.save_file):
                with open(self.save_file, 'r') as f:
                    data = json.load(f)
                print("Loaded data:", data)  # Debug print
                self.players = [Player.from_dict(p) for p in data["players"]]
                self.properties = [Property.from_dict(p) for p in data["properties"]]
                self.transaction_log = data.get("transactions", [])
                # Ensure properties are correctly assigned to players
                for player in self.players:
                    print("Player properties before assignment:", player.properties)  # Debug print
                    player.properties = [next(prop for prop in self.properties if prop.name == p.name) for p in player.properties]
                    print("Player properties after assignment:", player.properties)  # Debug print
                # Ensure owners are correctly assigned to properties
                for property in self.properties:
                    if property.owner:
                        print(f"Assigning owner for property {property.name}: {property.owner}")  # Debug print
                        property.owner = next(player for player in self.players if player.name == property.owner)
                        print(f"Owner assigned for property {property.name}: {property.owner.name}")  # Debug print
                messagebox.showinfo("Success", "Game loaded!")
                return True
            messagebox.showwarning("Warning", "No save file found!")
            return False
        except Exception as e:
            print("Error during load_game:", e)  # Debug print
            messagebox.showerror("Error", f"Load failed: {str(e)}")
            return False

class Player:
    def __init__(self, name):
        self.name = name
        self.money = 1500
        self.properties = []
        self.position = 0
        self.in_jail = False

    def add_property(self, property):
        self.properties.append(property)
        property.owner = self
        
    def remove_property(self, property):
        self.properties.remove(property)
        property.owner = None

    def to_dict(self):
        return {
            "name": self.name,
            "money": self.money,
            "properties": [property.to_dict() for property in self.properties],  # Convert properties to dictionaries
            "position": self.position,
            "in_jail": self.in_jail
        }

    @classmethod
    def from_dict(cls, data):
        print("Player data being loaded:", data)  # Debug print
        player = cls(data["name"])
        player.money = data["money"]
        player.properties = [Property.from_dict(p) if isinstance(p, dict) else p for p in data["properties"]]  # Convert property names to Property objects
        player.position = data["position"]
        player.in_jail = data["in_jail"]
        print("Player created:", player)  # Debug print
        return player