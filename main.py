from typing_extensions import Literal
from cmd import Cmd
from sys import exit

def stub(*args):
    print(f"Stub: {args}")

def TODO(s):
    print(f"TODO: {s}")

class Prompt(Cmd):
    intro = "Welcome to my unnammed adventure game, work is still in progress"
    prompt = ">"

    def __init__(self, starting_room : Room, *args):
        self.current_room =  starting_room
        super().__init__(*args)
    
    def do_go(self, arg):
        """
        Go in a Cardnal direction

        Use: go [direction]
        """
        direction = ""
        room = self.current_room
        if arg.lower() == "n" or arg.lower() == "north":
            direction = "North"
        elif arg.lower() == "e" or arg.lower() == "east":
            direction = "East"
        elif arg.lower() == "s" or arg.lower() == "south":
            direction = "South"
        elif arg.lower() == "w" or arg.lower() == "west":
            direction = "West"
        else:
            print(f"Not a valid direction, got '{arg}'")
            return

        travel = room.exits[direction]
        
        if travel is None:
            print(f"Sorry, you can't go {direction} here.")
            return
        self.current_room = travel
        self.do_look()
        return
            
        

    def do_look(self, arg = ""):
        """
        Look at the current area

        Usage: look
        """
        room = self.current_room

        print(f"Location: {room.name}")
        print(room.desc)

        exits = []

        for key, value in room.exits.items():
            if not value is None:
                exits.append(key)
            
        print(f"Available Directions: {", ".join(exits)}")
        
        return
    


    def do_shell(self, arg):
        """
        For debuging use, executes command as python code

        Usage: ![Command]

        Dev Note: this does not print expresions by default like an IDLE so a print statement is usualy needed
        """
        exec(arg, globals())
        return
    

    def do_exit(self, arg):
        """
        Exit the game

        Usage: exit

        Dev Note: A save system has not been implemented yet
        """
        exit()
        
        
    




class Room:
    _rooms = {}

    Direction = Literal["North", "East", "South", "West"]

    def __init__(self, name, desc : str = ""):
        self.desc = desc
        self.name = name
        self._registerRoom(self)

        self.exits = {"North": None, 
                      "East": None, 
                      "South": None, 
                      "West": None}

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

        _room1 = cls.getRoom(room1)
        _room2 = cls.getRoom(room2)
        
        _room1._connectRoom(_room2, exit1)
        _room2._connectRoom(_room1, exit2)

    @classmethod
    def getRoom(cls, room: str) -> Room:
        if room not in cls._rooms.keys():
            raise ValueError(f"{room} does not exist!")
        return cls._rooms[room]
        



Room("Start", "The start of the game")
Room("Building", "a non discript building =")
Room("Lawn", "There is green grass all around you")
Room("Front Pourch", "your not inside the building yet..")

Room.connect("Start", "North", "Lawn", "South")
Room.connect("Lawn", "West", "Front Pourch", "East")
Room.connect("Front Pourch", "West", "Building", "East")


if __name__ == "__main__":
    prompt = Prompt(Room.getRoom("Start"))
    prompt.cmdloop()