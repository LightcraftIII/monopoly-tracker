import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from core.player import Player  # Ensure correct import
from core.game_engine import MonopolyTracker
import csv
from tkinter.ttk import Combobox
import json

class MonopolyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Monopoly Tracker")
        self.tracker = MonopolyTracker()
        self.create_widgets()
        self.update_player_list()
        self._bind_shortcuts()
        self.loan_log = {}  # Initialize loan log
        self.bank_loans = {}  # Initialize bank loans
        self.load_game_data()  # Load game data including loans

    def _bind_shortcuts(self):
        self.root.bind("<Control-n>", self._debug_shortcut(self.add_player, "Ctrl+N"))
        self.root.bind("<Control-s>", self._debug_shortcut(lambda event: self.save_game(), "Ctrl+S"))
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
        ttk.Button(btn_frame, text="Assign Property", command=self.assign_property).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Pay Rent", command=self.pay_rent).grid(row=0, column=2, padx=5)
        ttk.Button(btn_frame, text="Toggle Jail", command=self.toggle_jail).grid(row=0, column=3, padx=5)
        ttk.Button(btn_frame, text="Loan", command=self.loan).grid(row=0, column=4, padx=5)
        ttk.Button(btn_frame, text="Sell Property", command=self.sell_property).grid(row=0, column=5, padx=5)
        ttk.Button(btn_frame, text="View Debt Log", command=self.view_debt_log).grid(row=0, column=6, padx=5)

        # Advanced Menu
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        advanced_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Advanced", menu=advanced_menu)
        advanced_menu.add_command(label="Update Money", command=self.update_money)
        advanced_menu.add_command(label="Player to Player Transaction", command=self.player_to_player_transaction)

        # Details Panel
        self.details_frame = ttk.LabelFrame(self.root, text="Player Details")
        self.details_frame.pack(pady=10, padx=10, fill=tk.BOTH)

        self.details_text = tk.Text(self.details_frame, height=10)
        self.details_text.pack(fill=tk.BOTH, expand=True)

        # Save/Load Buttons
        ttk.Button(self.root, text="Save Game", command=self.save_game).pack(side=tk.LEFT, padx=10)
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
        self.check_loans()

    def update_transaction_display(self):
        self.transaction_tree.delete(*self.transaction_tree.get_children())
        for entry in reversed(self.tracker.transaction_log[-50:]):
            self.transaction_tree.insert("", "end", values=(
                entry["timestamp"],
                entry["player"],
                f"${entry['amount']:+}",
                entry["reason"]
            ))
        self.transaction_tree.yview_moveto(0)  # Scroll to the top

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
            self.load_game_data()
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

    def player_to_player_transaction(self):
        payer = self.get_selected_player()
        if not payer:
            return

        transaction_dialog = tk.Toplevel(self.root)
        transaction_dialog.title("Player to Player Transaction")
        transaction_dialog.geometry("300x200")

        ttk.Label(transaction_dialog, text="Select Recipient:").pack(pady=10)
        recipient_names = [p.name for p in self.tracker.players if p != payer]
        if not recipient_names:
            messagebox.showinfo("Info", "No other players available")
            return

        recipient_combo = Combobox(transaction_dialog, values=recipient_names, state="readonly")
        recipient_combo.pack(pady=5)
        recipient_combo.current(0)

        ttk.Label(transaction_dialog, text="Enter Amount:").pack(pady=10)
        amount_entry = ttk.Entry(transaction_dialog)
        amount_entry.pack(pady=5)

        def on_transfer():
            recipient_name = recipient_combo.get()
            amount = amount_entry.get()
            if recipient_name and amount:
                try:
                    amount = int(amount)
                    if amount <= 0:
                        raise ValueError("Amount must be positive")
                    recipient = next(p for p in self.tracker.players if p.name == recipient_name)
                    if payer.money >= amount:
                        payer.money -= amount
                        recipient.money += amount
                        self.tracker.log_transaction(payer, -amount, f"Transferred to {recipient.name}")
                        self.tracker.log_transaction(recipient, amount, f"Received from {payer.name}")
                        self.update_display()
                        transaction_dialog.destroy()
                    else:
                        messagebox.showerror("Error", "Not enough money!")
                except ValueError as e:
                    messagebox.showerror("Error", str(e))

        ttk.Button(transaction_dialog, text="Transfer", command=on_transfer).pack(pady=10)

    def loan(self):
        loan_dialog = tk.Toplevel(self.root)
        loan_dialog.title("Loan")
        loan_dialog.geometry("300x200")

        ttk.Label(loan_dialog, text="Select Loan Type:").pack(pady=10)
        loan_type_combo = Combobox(loan_dialog, values=["From Player", "From Bank", "Repay Loan"], state="readonly")
        loan_type_combo.pack(pady=5)
        loan_type_combo.current(0)

        def on_select():
            loan_type = loan_type_combo.get()
            loan_dialog.destroy()
            if loan_type == "From Player":
                self.loan_from_player()
            elif loan_type == "From Bank":
                self.loan_from_bank()
            elif loan_type == "Repay Loan":
                self.repay_loan()

        ttk.Button(loan_dialog, text="Next", command=on_select).pack(pady=10)

    def loan_from_bank(self):
        borrower = self.get_selected_player()
        if not borrower:
            return

        if self.bank_loans.get(borrower.name, 0) >= 360:
            messagebox.showerror("Error", "You have reached the maximum loan limit from the bank!")
            return

        loan_dialog = tk.Toplevel(self.root)
        loan_dialog.title("Loan from Bank")
        loan_dialog.geometry("300x150")

        ttk.Label(loan_dialog, text="Enter Loan Amount (max 360):").pack(pady=10)
        amount_entry = ttk.Entry(loan_dialog)
        amount_entry.pack(pady=5)

        def on_loan():
            amount = amount_entry.get()
            if amount:
                try:
                    amount = int(amount)
                    if amount <= 0 or amount > 360:
                        raise ValueError("Amount must be between 1 and 360")
                    if self.bank_loans.get(borrower.name, 0) + amount > 360:
                        raise ValueError("Total loan amount exceeds 360")
                    borrower.money += amount
                    self.bank_loans[borrower.name] = self.bank_loans.get(borrower.name, 0) + amount
                    self.tracker.log_transaction(borrower, amount, "Loan from Bank")
                    self.update_display()
                    loan_dialog.destroy()
                except ValueError as e:
                    messagebox.showerror("Error", str(e))

        ttk.Button(loan_dialog, text="Loan", command=on_loan).pack(pady=10)

    def loan_from_player(self):
        borrower = self.get_selected_player()
        if not borrower:
            return

        loan_dialog = tk.Toplevel(self.root)
        loan_dialog.title("Loan from Player")
        loan_dialog.geometry("300x200")

        ttk.Label(loan_dialog, text="Select Lender:").pack(pady=10)
        lender_names = [p.name for p in self.tracker.players if p != borrower]
        if not lender_names:
            messagebox.showinfo("Info", "No other players available")
            return

        lender_combo = Combobox(loan_dialog, values=lender_names, state="readonly")
        lender_combo.pack(pady=5)
        lender_combo.current(0)

        ttk.Label(loan_dialog, text="Enter Loan Amount:").pack(pady=10)
        amount_entry = ttk.Entry(loan_dialog)
        amount_entry.pack(pady=5)

        def on_loan():
            lender_name = lender_combo.get()
            amount = amount_entry.get()
            if lender_name and amount:
                try:
                    amount = int(amount)
                    if amount <= 0:
                        raise ValueError("Amount must be positive")
                    lender = next(p for p in self.tracker.players if p.name == lender_name)
                    if lender.money >= amount:
                        lender.money -= amount
                        borrower.money += amount
                        self.tracker.log_transaction(lender, -amount, f"Loaned to {borrower.name}")
                        self.tracker.log_transaction(borrower, amount, f"Loan from {lender.name}")
                        self.loan_log.setdefault(borrower.name, []).append({"lender": lender.name, "amount": amount})
                        self.update_display()
                        loan_dialog.destroy()
                    else:
                        messagebox.showerror("Error", "Lender does not have enough money!")
                except ValueError as e:
                    messagebox.showerror("Error", str(e))

        ttk.Button(loan_dialog, text="Loan", command=on_loan).pack(pady=10)

    def repay_loan(self):
        borrower = self.get_selected_player()
        if not borrower:
            return

        repay_dialog = tk.Toplevel(self.root)
        repay_dialog.title("Repay Loan")
        repay_dialog.geometry("300x200")

        ttk.Label(repay_dialog, text="Select Lender:").pack(pady=10)
        lender_names = [loan["lender"] for loan in self.loan_log.get(borrower.name, [])]
        if borrower.name in self.bank_loans:
            lender_names.append("Bank")
        if not lender_names:
            messagebox.showinfo("Info", "No loans to repay")
            return

        lender_combo = Combobox(repay_dialog, values=lender_names, state="readonly")
        lender_combo.pack(pady=5)
        lender_combo.current(0)

        def on_repay():
            lender_name = lender_combo.get()
            if lender_name == "Bank":
                amount = self.bank_loans.get(borrower.name, 0)
                if amount and borrower.money >= amount:
                    borrower.money -= amount
                    del self.bank_loans[borrower.name]
                    self.tracker.log_transaction(borrower, -amount, "Repayment to Bank")
                    self.update_display()
                    repay_dialog.destroy()
                else:
                    messagebox.showerror("Error", "Not enough money to repay the bank!")
            else:
                loan = next((loan for loan in self.loan_log[borrower.name] if loan["lender"] == lender_name), None)
                if loan and borrower.money >= loan["amount"]:
                    lender = next(p for p in self.tracker.players if p.name == lender_name)
                    borrower.money -= loan["amount"]
                    lender.money += loan["amount"]
                    self.tracker.log_transaction(borrower, -loan["amount"], f"Repayment to {lender.name}")
                    self.tracker.log_transaction(lender, loan["amount"], f"Repayment from {borrower.name}")
                    self.loan_log[borrower.name].remove(loan)
                    self.update_display()
                    repay_dialog.destroy()
                else:
                    messagebox.showerror("Error", "Not enough money to repay the loan!")

        ttk.Button(repay_dialog, text="Repay", command=on_repay).pack(pady=10)

    def check_loans(self):
        for borrower_name, loans in self.loan_log.items():
            borrower = next(p for p in self.tracker.players if p.name == borrower_name)
            for loan in loans:
                if borrower.money >= loan["amount"]:
                    lender = next(p for p in self.tracker.players if p.name == loan["lender"])
                    if messagebox.askyesno("Loan Repayment", f"{borrower.name} has enough funds to repay {loan['amount']} to {lender.name}. Do you want to process the repayment?"):
                        borrower.money -= loan["amount"]
                        lender.money += loan["amount"]
                        self.tracker.log_transaction(borrower, -loan["amount"], f"Repayment to {lender.name}")
                        self.tracker.log_transaction(lender, loan["amount"], f"Repayment from {borrower.name}")
                        loans.remove(loan)
                        self.update_display()

    def view_debt_log(self):
        debt_log_dialog = tk.Toplevel(self.root)
        debt_log_dialog.title("Debt Log")
        debt_log_dialog.geometry("400x300")

        debt_log_text = tk.Text(debt_log_dialog, height=15)
        debt_log_text.pack(fill=tk.BOTH, expand=True)

        debt_log_text.insert(tk.END, "Debt Log:\n")
        for borrower_name in set(self.loan_log.keys()).union(self.bank_loans.keys()):
            debt_log_text.insert(tk.END, f"\n{borrower_name}:\n")
            if borrower_name in self.loan_log:
                for loan in self.loan_log[borrower_name]:
                    debt_log_text.insert(tk.END, f"  Owes {loan['amount']} to {loan['lender']}\n")
            if borrower_name in self.bank_loans:
                debt_log_text.insert(tk.END, f"  Owes {self.bank_loans[borrower_name]} to the Bank\n")

        debt_log_text.config(state=tk.DISABLED)

    def save_game(self):
        self.tracker.save_game()
        self.save_game_data()

    def save_game_data(self):
        data = {
            "loan_log": self.loan_log,
            "bank_loans": self.bank_loans
        }
        with open("game_data.json", "w") as f:
            json.dump(data, f)

    def load_game_data(self):
        try:
            with open("game_data.json", "r") as f:
                data = json.load(f)
                self.loan_log = data.get("loan_log", {})
                self.bank_loans = data.get("bank_loans", {})
        except FileNotFoundError:
            pass

    def sell_property(self):
        seller = self.get_selected_player()
        if not seller:
            return

        sell_dialog = tk.Toplevel(self.root)
        sell_dialog.title("Sell Property")
        sell_dialog.geometry("300x200")

        owned_props = [p for p in seller.properties]
        if not owned_props:
            messagebox.showinfo("Info", "No properties to sell")
            return

        ttk.Label(sell_dialog, text="Select Property:").pack(pady=10)
        prop_names = [str(p) for p in owned_props]
        prop_combo = Combobox(sell_dialog, values=prop_names, state="readonly")
        prop_combo.pack(pady=5)
        prop_combo.current(0)

        ttk.Label(sell_dialog, text="Select Buyer:").pack(pady=10)
        buyer_names = [p.name for p in self.tracker.players if p != seller]
        buyer_combo = Combobox(sell_dialog, values=buyer_names, state="readonly")
        buyer_combo.pack(pady=5)
        buyer_combo.current(0)

        ttk.Label(sell_dialog, text="Enter Sale Price:").pack(pady=10)
        price_entry = ttk.Entry(sell_dialog)
        price_entry.pack(pady=5)

        def on_sell():
            prop_name = prop_combo.get()
            buyer_name = buyer_combo.get()
            price = price_entry.get()
            if prop_name and buyer_name and price:
                try:
                    price = int(price)
                    if price <= 0:
                        raise ValueError("Price must be positive")
                    prop = next(p for p in owned_props if str(p) == prop_name)
                    buyer = next(p for p in self.tracker.players if p.name == buyer_name)
                    if buyer.money >= price:
                        seller.money += price
                        buyer.money -= price
                        seller.remove_property(prop)
                        buyer.add_property(prop)
                        self.tracker.log_transaction(seller, price, f"Sold {prop.name} to {buyer.name}")
                        self.tracker.log_transaction(buyer, -price, f"Bought {prop.name} from {seller.name}")
                        self.update_display()
                        sell_dialog.destroy()
                    else:
                        messagebox.showerror("Error", "Buyer does not have enough money!")
                except ValueError as e:
                    messagebox.showerror("Error", str(e))

        ttk.Button(sell_dialog, text="Sell", command=on_sell).pack(pady=10)