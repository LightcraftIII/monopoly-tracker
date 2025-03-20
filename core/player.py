class Player:
    def __init__(self, name):
        self.name = name
        self.money = 1500
        self.properties = []
        self.position = 0
        self.in_jail = False

    def to_dict(self):
        return {
            'name': self.name,
            'money': self.money,
            'properties': self.properties,
            'position': self.position,
            'in_jail': self.in_jail
        }

    @classmethod
    def from_dict(cls, data):
        player = cls(data['name'])
        player.money = data['money']
        player.properties = data['properties']
        player.position = data['position']
        player.in_jail = data['in_jail']
        return player