from typing_extensions import Literal



class Room:
    _rooms = {}

    Direction = Literal["North", "East", "South", "West"]

    def __init__(self, name):
        self.name = name
        self._registerRoom(self)

        self.exits = {"North": None, 
                      "East": None, 
                      "South": None, 
                      "West": None}

        return self
    @classmethod
    def _registerRoom(cls, room: Room):
        if room.name in cls._rooms.keys():
            raise ValueError(f"Room with name {room.name} already exists")
        cls._rooms[room.name] = room
        return room

    @classmethod
    def getRooms(cls):
        return list(cls._rooms.keys())

    def _connectRoom(self, connection: Room, direction: Direction):
        if self.exits[direction] is not None:
            raise ValueError(f"Direction {direction} is clamed in {self.name} and cant connect to {connection.name}")
        else:
            self.exits[direction] = connection

    @classmethod
    def connect(cls, room1: str, exit1: Direction, room2: str, exit2: Direction):

        type _room1 = Room
        type _room2 = Room

        _room1 = cls.getRoom[room1]
        _room2 = cls.getRoom[room2]
        
        _room1._connectRoom(_room2, exit1)
        _room2._connectRoom(_room1, exit2)

    @classmethod
    def getRoom(cls, room: str) -> Room:
        if room not in cls._rooms.keys():
            raise ValueError(f"{room} does not exist!")
        return cls._rooms[room]
        



Room("Start")
Room("Building")
Room("Lawn")
Room("Front Pourch")

Room.connect("Start", "North", "Lawn", "South")
Room.connect("Lawn", "West", "Front Pourch", "East")
Room.connect("Front Pourch", "West", "Building", "East")

if __name__ == "__main__":
    loop = True
else:
    loop = False

while loop:
    room = Room.getRoom("Start")
    print(f"You are in {room.name}")
    # TODO: get availible directions
    # TODO: get user input and turn it to a command
