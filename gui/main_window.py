import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from core.player import Player  # Ensure correct import
from core.game_engine import MonopolyTracker
import csv
from tkinter.ttk import Combobox

class MonopolyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Monopoly Tracker")
        self.tracker = MonopolyTracker()
        self.create_widgets()
        self.update_player_list()
        self._bind_shortcuts()

    def _bind_shortcuts(self):
        self.root.bind("<Control-n>", self._debug_shortcut(self.add_player, "Ctrl+N"))
        self.root.bind("<Control-s>", self._debug_shortcut(lambda event: self.tracker.save_game(), "Ctrl+S"))
        self.root.bind("<Control-l>", self._debug_shortcut(self.load_game, "Ctrl+L"))
        self.details_text.bind("<Control-n>", lambda e: "break")
        self.details_text.bind("<Control-s>", lambda e: "break")
        self.details_text.bind("<Control-l>", lambda e: "break")

    def _debug_shortcut(self, func, name):
        def wrapper(event):
            print(f"Shortcut {name} triggered")
            func(event)
        return wrapper

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
        ttk.Button(btn_frame, text="Assign Property", command=self.assign_property).grid(row=0, column=2, padx=5)
        ttk.Button(btn_frame, text="Pay Rent", command=self.pay_rent).grid(row=0, column=3, padx=5)
        ttk.Button(btn_frame, text="Toggle Jail", command=self.toggle_jail).grid(row=0, column=4, padx=5)

        # Details Panel
        self.details_frame = ttk.LabelFrame(self.root, text="Player Details")
        self.details_frame.pack(pady=10, padx=10, fill=tk.BOTH)

        self.details_text = tk.Text(self.details_frame, height=10)
        self.details_text.pack(fill=tk.BOTH, expand=True)

        # Save/Load Buttons
        ttk.Button(self.root, text="Save Game", command=self.tracker.save_game).pack(side=tk.LEFT, padx=10)
        ttk.Button(self.root, text="Load Game", command=self.load_game).pack(side=tk.RIGHT, padx=10)

        # Transaction History
        self.transaction_frame = ttk.LabelFrame(self.root, text="Transaction History")
        self.transaction_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        self.transaction_tree = ttk.Treeview(self.transaction_frame, 
            columns=("Time", "Player", "Amount", "Reason"), show="headings")

        for col in ("Time", "Player", "Amount", "Reason"):
            self.transaction_tree.heading(col, text=col)

        vsb = ttk.Scrollbar(self.transaction_frame, orient="vertical", command=self.transaction_tree.yview)
        self.transaction_tree.configure(yscrollcommand=vsb.set)

        self.transaction_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        ttk.Button(self.transaction_frame, text="Export CSV", command=self.export_transactions).pack(pady=5)

    def update_player_list(self):
        self.player_list.delete(0, tk.END)
        for player in self.tracker.players:
            self.player_list.insert(tk.END, player.name)

    def show_player_details(self, event=None):
        selection = self.player_list.curselection()
        if not selection:
            return

        player = self.tracker.players[selection[0]]
        print("Selected player:", player)  # Debug print
        properties = "\n".join(f"• {prop.name}" for prop in player.properties) if player.properties else "None"
        print("Player properties:", properties)  # Debug print

        details = (
            f"Name: {player.name}\n"
            f"Money: ${player.money}\n"
            f"Properties:\n{properties}\n"
            f"Position: {player.position}\n"
            f"Jail Status: {'In Jail' if player.in_jail else 'Free'}"
        )

        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(tk.END, details)

    def get_selected_player(self):
        selection = self.player_list.curselection()
        if not selection:
            messagebox.showwarning("Warning", "No player selected!")
            return None
        return self.tracker.players[selection[0]]

    def assign_property(self):
        player = self.get_selected_player()
        if not player:
            return

        assign_dialog = tk.Toplevel(self.root)
        assign_dialog.title("Assign Property")
        assign_dialog.geometry("300x150")

        available = [p for p in self.tracker.properties if not p.owner]
        if not available:
            messagebox.showinfo("Info", "No available properties")
            return

        ttk.Label(assign_dialog, text="Select Property:").pack(pady=10)
        prop_names = [str(p) for p in available]
        combo = Combobox(assign_dialog, values=prop_names, state="readonly")
        combo.pack(pady=5)
        combo.current(0)

        def on_assign():
            selected = combo.get()
            if selected:
                prop = next(p for p in available if str(p) == selected)
                if player.money >= prop.price:
                    player.money -= prop.price  # Subtract property price from player's money
                    player.add_property(prop)
                    self.tracker.log_transaction(player, -prop.price, f"Purchased {prop.name}")
                    self.update_display()
                    self.show_player_details()  # Ensure player details are updated
                    assign_dialog.destroy()
                else:
                    messagebox.showerror("Error", "Not enough money!")

        ttk.Button(assign_dialog, text="Assign", command=on_assign).pack(pady=10)

    def pay_rent(self):
        payer = self.get_selected_player()
        if not payer:
            return

        rent_dialog = tk.Toplevel(self.root)
        rent_dialog.title("Pay Rent")
        rent_dialog.geometry("300x150")

        owned_props = [p for p in self.tracker.properties if p.owner and p.owner != payer]
        if not owned_props:
            messagebox.showinfo("Info", "No owned properties to pay rent on")
            return

        ttk.Label(rent_dialog, text="Select Property:").pack(pady=10)
        prop_names = [str(p) for p in owned_props]
        combo = Combobox(rent_dialog, values=prop_names, state="readonly")
        combo.pack(pady=5)
        combo.current(0)

        def on_pay():
            selected = combo.get()
            if selected:
                prop = next(p for p in owned_props if str(p) == selected)
                self.tracker.charge_rent(payer, prop)
                self.update_display()
                rent_dialog.destroy()

        ttk.Button(rent_dialog, text="Pay Rent", command=on_pay).pack(pady=10)

    def update_display(self):
        self.update_player_list()
        self.show_player_details()
        self.update_transaction_display()

    def update_transaction_display(self):
        self.transaction_tree.delete(*self.transaction_tree.get_children())
        for entry in reversed(self.tracker.transaction_log[-50:]):
            self.transaction_tree.insert("", "end", values=(
                entry["timestamp"],
                entry["player"],
                f"${entry['amount']:+}",
                entry["reason"]
            ))
        self.transaction_tree.yview_moveto(1)

    def export_transactions(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")]
        )
        if filename:
            try:
                with open(filename, 'w', newline='') as f:
                    fieldnames = ["timestamp", "player", "amount", "new_balance", "reason"]
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(self.tracker.transaction_log)
                messagebox.showinfo("Success", "Transactions exported!")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {str(e)}")

    def add_player(self, event=None):
        name = simpledialog.askstring("Add Player", "Enter player name:")
        if name:
            if any(p.name.lower() == name.lower() for p in self.tracker.players):
                messagebox.showerror("Error", "Player already exists!")
            else:
                new_player = Player(name)
                self.tracker.players.append(new_player)
                self.tracker.log_transaction(new_player, 0, "Player created")
                self.update_display()

    def update_money(self):
        player = self.get_selected_player()
        if not player:
            return

        amount = simpledialog.askinteger("Update Money", "Amount (+/-):")
        if amount:
            player.money += amount
            self.tracker.log_transaction(player, amount, "Manual adjustment")
            self.update_display()

    def toggle_jail(self):
        player = self.get_selected_player()
        if player:
            player.in_jail = not player.in_jail
            status = "Jailed" if player.in_jail else "Released"
            self.tracker.log_transaction(player, 0, status)
            self.update_display()

    def load_game(self, event=None):
        if self.tracker.load_game():
            self.update_display()

    def move_player(self):
        player = self.get_selected_player()
        if not player:
            return

        spaces = simpledialog.askinteger("Move Player", "Enter spaces to move:")
        if spaces:
            player.position = (player.position + spaces) % 40
            self.update_display()

    def update_property_list(self):
        # Assuming you have a Listbox or similar widget to display properties
        self.property_listbox.delete(0, 'end')
        for property in self.tracker.properties:
            self.property_listbox.insert('end', property.name)