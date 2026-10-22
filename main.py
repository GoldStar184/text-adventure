from typing import Literal
from cmd import Cmd

DEBUG = True

Direction = Literal["North", "East", "South", "West"] # I will probabbly add "Up" and "Down" later


def stub(*args): #when im done this should have no uses
    print(f"Stub: {args}")

def TODO(s):
    print(f"TODO: {s}") #same here

class Game(Cmd):
    """
    This is the Class that controlls gamestate and also user input at the same time
        this is because we are subclassing `Cmd` to provide user input as a good system 
        so I dont have to write a help system and figure out how to write diffrent 
        commands that go to diffrent functions. But because the input loop is here, I found 
        it easier to just store gamestate here in the same loop. (Yes I could have technicly 
        made a dataclass for gamestate but I realy dont want to do that)
    """
    # TODO: write better docstring

    intro = "Welcome to my unnammed adventure game, work is still in progress"
    prompt = ">"

    def __init__(self, starting_room : Room, *args):
        self.current_room =  starting_room
        super().__init__(*args)

        self.items: list[Item] = []
    
    def do_go(self, arg: str):
        """
        Go in a Cardnal direction

        Use: go [direction]
        """
        direction = ""
        room = self.current_room

        low_arg = arg.lower()

        if low_arg == "n" or low_arg == "north":
            direction = "North"
        elif low_arg == "e" or low_arg == "east":
            direction = "East"
        elif low_arg == "s" or low_arg == "south":
            direction = "South"
        elif low_arg == "w" or low_arg == "west":
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
        return False
            
        

    def do_look(self, arg = ""):
        """
        Look at the current area

        Usage: look
        """
        room = self.current_room

        if arg == "" or arg == "Room" or arg == room.name:


            print(f"Location: {room.name}")
            print(room.desc)

            exits = []

            for key, value in room.exits.items():
                if not value is None:
                    exits.append(key)

                
            print(f"Available Directions: {", ".join(exits)}")

            if len(room.items) != 0:
                items = [i.name for i in room.items]
                print(f"Items: {", ".join(items)}")

            if len(room.objects) != 0:
                objects = [i.name for i in room.objects]
                print(f"Objects: {", ".join(objects)}")

            return False
        else:
            TODO("Look at items and objects")

            #TODO: look at items and objects

    

    if DEBUG:
        def do_shell(self, arg):
            """
            For debuging use, executes command as python code

            Usage: ![Command]

            Dev Note: this does not print expresions by default like an IDLE so a print statement is usualy needed
            Dev Note 2: Dont even try to write fuctions or anything that needs multiple lines here.
            """
            exec(arg, globals())
            return False

    def do_use(self, arg):
        """
        Use an Item or Object

        """
        inp = arg.lower().strip()

        # Keys are handeled specially
        if "key" in inp: 
            # This allows the player to attempt to use the wrong key, but it will auto use the right one
            # TODO: fix this edge case

            #Get all keys
            keys = [key for key in self.items if isinstance(key, Key)]

            if len(keys) == 0:
                print("You dont have any keys!")
                return False
            
            doors = [door for door in self.current_room.objects if isinstance(door, Door)]

            if len(doors) == 0:
                print("There is no place to use a key here!")
                return False

            for door in doors:
                for key in keys:
                    if key.descriptor == door.descriptor and door.locked:
                        key.use(self, door)
                        self.items.remove(key)
                        return False
            print("Sorry, you don't have the correct key")
            return False
        # End key logic
        
        
        # Get all items and objects that match the input
        
        #TODO: turn valid checker into a function for eaiser readability and reusablity
        valid: list[Item | Object] = [i for i in self.current_room.objects + self.items if inp in i.name.lower()] # I am very proud of this elegent solution

        if len(valid) == 0:
            print(f"I dont know what a '{arg}' is.")
        elif len(valid) == 1:
            valid[0].use(self)
        else:
            print("Sorry, you will have to be more specific.")
        return False

    def do_grab(self, arg: str):
        """
        Grab a Item that is in the room
        """
        inp = arg.strip().lower()

        if inp == "":
            print("What do you want to grab?")
            return False
        if len(self.current_room.items) == 0:
            print("There are no Items here to grab.")
            return False
            
        valid: list[Item] = [i for i in self.current_room.items if inp in i.name.lower()]

        if len(valid) == 0:
            print(f"I Can't find a '{arg}' here.")
        elif len(valid) == 1:
            print(f"You Grabbed the {valid[0].name}!")
            self.items.append(valid.pop())
        else:
            print("Sorry, you will have to be more specific.")
        return False


    def do_exit(self, arg=""):
        """
        Exit the game

        Usage: exit

        Dev Note: A save system has not been implemented yet
        """
        return True
    
    def do_EOF(self, arg):
        """
        an alias of exit
        """
        return self.do_exit()



class Room:
    """
    This class represents a room (duh)
    It has refrences to other rooms based on direction.

    The Room class has its own internal refrence function so it should not be needed
        to to assign to a variable. instead use `Room.get([room name])` to get a refrence 
        to a room, though the `Room.connect` method takes a room name and not the refrence 
        to make writing all of the connections easier. (I will probably add support for directly
        giving a `Room` object later)

    Please be aware of the class methods, `Room.connect()` and `Room.get()` they do not need 
        to be called from a Room object and are designed to be called directly from `Room`
    """
    # TODO: write better docstring
    _rooms = {}



    def __init__(self, name, desc : str = "", items : list[Item] = [], objects : list[Object] = []):
        self.desc = desc
        self.name = name
        self.items = items.copy()
        self.objects = objects.copy()
        self._register(self)

        self.exits = {"North": None, 
                      "East": None, 
                      "South": None, 
                      "West": None}

    @classmethod
    def _register(cls, room: Room) -> None:
        if room.name in cls._rooms.keys():
            raise ValueError(f"Room with name {room.name} already exists")
        cls._rooms[room.name] = room
        return 

    @classmethod
    def getRooms(cls) -> list[str]:
        """
        Gets a list of room names.
        """
        return list(cls._rooms.keys())

    def _connectRoom(self, connection: Room, direction: Direction) -> None:
        if self.exits[direction] is not None:
            raise ValueError(f"Direction {direction} is claimed in {self.name} and cant connect to {connection.name}")
        else:
            self.exits[direction] = connection


    @classmethod
    def connect(cls, room1: str, exit1: Direction, room2: str, exit2: Direction) -> None:
        """
        Connect 2 rooms together
        Arguments:
            room1: a string, the name of the first room you want to connect.
            exit1: a string/Direction. What exit from room1 will leed to room2?
            room2: a string, the name of the second room you want to connect.
            exit2: a string/Direction. What exit from room2 will leed to room1?
        """

        type _room1 = Room
        type _room2 = Room

        _room1 = cls.get(room1)
        _room2 = cls.get(room2)

        
        _room1._connectRoom(_room2, exit1)
        _room2._connectRoom(_room1, exit2)

    @classmethod
    def get(cls, room: str) -> Room:
        """
        Gets a room from its name

        will raise `ValueError` if the room name does not exist
        """
        if room not in cls._rooms.keys():
            raise ValueError(f"{room} does not exist!")
        return cls._rooms[room]
        
class Item:
    """
    The Item class is for things that the player can pick up.

    This should not be directly used but subclassed into specific items.

    There is currently a limitation that the player can only have one of an Item at a time
    """
    type items = dict[str, Item]
    items = {}
    def __init__(self, name: str):
        self.name = name
        self._register(self)
        pass

    def use(self, game: Game) -> None:
        """
        Whatever happens when you use this item,
        This should be overridded by a subclass
        """
        pass

    @classmethod
    def _register(cls, item : Item) -> None:
        if item.name in cls.items.keys():
            raise ValueError(f"Item {item.name} already exists!")
        
        cls.items[item.name] = item
        return
    
    @classmethod
    def get(cls, item_name: str) -> Item:
        """
        Get an Item by its name.
        """
        if item_name in cls.items.keys():
            return cls.items[item_name]
        else:
            raise ValueError(f"Item, {item_name} does not exist!")
    


class Object:

    objects: dict[str, Object] = {}

    def __init__(self, name: str, desc: str):
        """
        An object that exists that the player can interact with but not pickup and take, 
        can also be seen by items like keys

        Like `Items` this should not be used by itself but subclassed into a more specific object
        """
        self.name = name
        self.desc = desc
        self._register(self)

    def use(self, game: Game) -> None:
        """
        Whatever happens when you use this object,
        This should be overridded by a subclass
        """
        pass
    
    @classmethod
    def _register(cls, object : Object) -> None:
        if object.name in cls.objects.keys():
            raise ValueError(f"Object {object.name} already exists!")
        
        cls.objects[object.name] = object
        return
    
    @classmethod
    def get(cls, object_name: str) -> Object:
        """
        Get an Object by its name.
        """
        if object_name in cls.objects.keys():
            return cls.objects[object_name]
        else:
            raise ValueError(f"Item, {object_name} does not exist!")

class Door(Object):
    def __init__(self, name: str, desc: str, descriptor: str):
        self.locked = True
        self.descriptor = descriptor
        super().__init__(name, desc) 
        # IDEA: we might want to allow desc to be a function to dynamacly change the discription

    def use(self, game: Game) -> None:
        """
        We need to use the key not the door, so print a message saying
            the door is locked
        """
        if self.locked:
            print("The door is locked")
    
    def connect(self, room1: str, exit1: Direction, room2: str, exit2: Direction, add_door=True) -> None:
        """
        see the docs for `Room.connect()` this is just a wrapper that stores all of
            the values for running `unlock` later.
        """

        _room1: Room = Room.get(room1)
        _room2: Room = Room.get(room2)

        self.room1: Room = _room1
        self.room2: Room = _room2
        self.exit1: Direction = exit1
        self.exit2: Direction = exit2

        if add_door:
            for room in [_room1, _room2]:
                room.objects.append(self)

    def unlock(self) -> None:
        """
        unlocks the door. normaly called by a key
        """
        # This is so inefficient, ill prob fix this later to accept room objects
        Room.connect(self.room1.name, self.exit1, self.room2.name, self.exit2)
        self.locked = False
        print("[PLACEHOLDER] The door has unlocked!")

        


class Key(Item):
    def __init__(self, name: str, descriptor: str):
        self.descriptor = descriptor
        super().__init__(name)

    def use(self, game: Game, door: Door | None = None) -> None:
        # The Key use method is only called when the use code above finds a matching door.
        if door is not None:
            door.unlock()
        else:
            TODO("specific key logic")
        


## --- Time to start creating all of the objects --- ##

# Items
Key("Red Key", "Red")
Door("Red Door", "A Red Door blockes your path inside", "Red")


# Rooms
Room("Start", "The start of the game")
Room("Building", "a non descript building")
Room("Lawn", "There is green grass all around you", items=[Item.get("Red Key")])
Room("Front Porch", "you are not inside the building yet..")


## --- Connecting objects to eachother --- ##

# Rooms
Room.connect("Start", "North", "Lawn", "South")
Room.connect("Lawn", "West", "Front Porch", "East")

Object.get("Red Door").connect("Front Porch", "West", "Building", "East") # Conditional unlock.


if __name__ == "__main__":
    game = Game(Room.get("Start"))
    game.cmdloop()