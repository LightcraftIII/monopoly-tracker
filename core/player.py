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