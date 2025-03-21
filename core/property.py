class Property:
    def __init__(self, name, price, rent, color_group, owner=None):
        self.name = name
        self.price = price
        self.rent = rent
        self.color_group = color_group
        self.owner = owner

    def calculate_rent(self):
        # Assuming rent is a list and we want to return the first element
        return int(self.rent[0]) if isinstance(self.rent, list) else int(self.rent)

    def to_dict(self):
        return {
            "name": self.name,
            "price": self.price,
            "rent": self.rent,
            "color_group": self.color_group,
            "owner": self.owner.name if self.owner else None
        }

    @classmethod
    def from_dict(cls, data):
        print("Property data being loaded:", data)  # Debug print
        property = cls(data["name"], data["price"], data["rent"], data["color_group"])
        property.owner = data["owner"]  # Store owner as a string initially
        print("Property created:", property)  # Debug print
        return property

    def __str__(self):
        return self.name