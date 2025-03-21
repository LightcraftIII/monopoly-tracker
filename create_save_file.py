import json
import os

def create_save_file(filepath):
    data = {
        "players": [
            {
                "name": "John",
                "money": 1300,
                "properties": [
                    {
                        "name": "Rue de la Paix",
                        "price": 400,
                        "rent": [50, 200, 600, 1400, 1700, 2000],
                        "color_group": "Dark Blue",
                        "owner": "John"
                    }
                ],
                "position": 0,
                "in_jail": False
            },
            {
                "name": "Jane",
                "money": 1450,
                "properties": [],
                "position": 0,
                "in_jail": False
            }
        ],
        "properties": [
            {
                "name": "Rue de la Paix",
                "price": 400,
                "rent": [50, 200, 600, 1400, 1700, 2000],
                "color_group": "Dark Blue",
                "owner": "John"
            },
            {
                "name": "Avenue des Champs-Élysées",
                "price": 350,
                "rent": [35, 175, 500, 1100, 1300, 1500],
                "color_group": "Dark Blue",
                "owner": None
            }
            # Add more properties as needed
        ],
        "transactions": [
            {
                "timestamp": "2025-03-21 17:32:27",
                "player": "Bank",
                "amount": 400,
                "reason": "Created Rue de la Paix"
            },
            {
                "timestamp": "2025-03-21 17:32:30",
                "player": "John",
                "amount": 0,
                "new_balance": 1500,
                "reason": "Player created"
            },
            {
                "timestamp": "2025-03-21 17:32:42",
                "player": "John",
                "amount": -400,
                "new_balance": 1100,
                "reason": "Purchased Rue de la Paix"
            },
            {
                "timestamp": "2025-03-21 17:32:59",
                "player": "Jane",
                "amount": -50,
                "new_balance": 1450,
                "reason": "Paid rent for Rue de la Paix"
            },
            {
                "timestamp": "2025-03-21 17:32:59",
                "player": "John",
                "amount": 50,
                "new_balance": 1150,
                "reason": "Received rent for Rue de la Paix"
            }
        ]
    }

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Save file created at {filepath}")

if __name__ == "__main__":
    filepath = "c:\\Users\\ADMIN\\Desktop\\Monopoly\\V2\\data\\saved_games\\latest.json"
    create_save_file(filepath)
