import json

def load_saved_game(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data

def print_players_and_properties(data):
    players = data.get("players", [])
    for player in players:
        print(f"Player: {player['name']}")
        print(f"Money: ${player['money']}")
        properties = player.get("properties", [])
        if properties:
            print("Properties:")
            for prop in properties:
                print(f"  - {prop['name']}")
        else:
            print("Properties: None")
        print()

if __name__ == "__main__":
    filepath = "c:\\Users\\ADMIN\\Desktop\\Monopoly\\V2\\data\\saved_games\\latest.json"
    data = load_saved_game(filepath)
    print_players_and_properties(data)
