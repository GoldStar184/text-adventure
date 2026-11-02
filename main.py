from typing import Literal, Optional, Sequence, TypeVar
from cmd import Cmd
from abc import ABC, abstractmethod
from sys import hexversion
from random import randint, choice

if hexversion < 51315184: #Developed in python 3.15.1
    print(f"You are Running an earlier version of python than was used to develop this game, bugs may be present")

DEBUG = True

Direction = Literal["North", "East", "South", "West"] # I will probably add "Up" and "Down" later
SearchItem = TypeVar("SearchItem", bound="Object | Item")

def TODO(s): #when im done this should have no uses
    print(f"TODO: {s}")

class Game(Cmd):
    """
    This is the Class that controls game state and also user input at the same time
        this is because we are subclassing `Cmd` to provide user input as a good system 
        so I dont have to write a help system and figure out how to write different 
        commands that go to different functions. But because the input loop is here, I found 
        it easier to just store game state here in the same loop. (Yes I could have technically 
        made a dataclass for game state but I really dont want to do that)
    """
    # TODO: write better docstring

    intro = """Welcome to my unnamed adventure game, work is still in progress
If this is your first time playing read the introduction sign by typing 'read sign'
For help type `help`"""# Why do indented multi line strings have to be written like this?
    prompt = "> "

    specific = "Sorry, you will have to be more specific."

    def __init__(self, starting_room : Room, *args):
        self.current_room =  starting_room
        self.flags: dict[str, bool] = {"homework": False, "teeth": False} # Need to check if HW is done, but will write to be extendable
        super().__init__(*args)

        self.items: list[Item] = []
    def find_valid(self, substring: str, search: Sequence[SearchItem]) -> list[SearchItem]:
        # I am very proud of this. Its a very elegant solution.
        return [item for item in search if substring in item.name.lower()]
    
    def do_go(self, arg: str):
        """
        Go in a Cardinal direction

        Use: go [direction]
        """
        direction = ""
        room = self.current_room

        low_arg = arg.lower()

        direction_map: dict[str, Direction] = { "n": "North", "north": "North",
                                                "e": "East", "east": "East", 
                                                "s": "South", "south": "South",
                                                "w": "West", "west": "West"}

        if low_arg not in direction_map.keys():
            print(f"Not a valid direction, got '{arg}'")
            return False
        else:
            direction = direction_map[low_arg]

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

            inp = arg.strip().lower()
            valid = self.find_valid(inp, self.items + self.current_room.objects)

            if len(valid) == 0:
                print(f"Sorry, I don't know what a '{arg}' is")
            elif len(valid) > 1:
                print(self.specific)
            else:
                print(f"{type(valid[0]).__name__}: {valid[0].name}")
                print(valid[0].desc)
            return False

    def do_use(self, arg):
        """
        Use an Item or Object

        """
        inp = arg.lower().strip()

        # Auto use the correct key
        if inp == "key": 

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
        
        
        valid = self.find_valid(inp, self.items + self.current_room.objects)

        if len(valid) == 0:
            print(f"I dont know what a '{arg}' is.")
        elif len(valid) == 1:
            valid[0].use(self)
        else:
            print(self.specific)
        return False

    def do_grab(self, arg: str):
        """
        Grab a Item that is in the room

        Usage: grab <item>
        """
        inp = arg.strip().lower()

        if inp == "":
            print("What do you want to grab?")
            return False
        if len(self.current_room.items) == 0:
            print("There are no Items here to grab.")
            return False
            
        valid: list[Item] = self.find_valid(inp, self.current_room.items)

        if len(valid) == 0:
            print(f"I Can't find a '{arg}' here.")
        elif len(valid) == 1:
            print(f"You Grabbed the {valid[0].name}!")
            self.items.append(valid[0])
            self.current_room.items.remove(valid[0])
        else:
            print(self.specific)
        return False

    def do_read(self, arg: str):
        """
        Read an Object or Item

        Usage: read <Name>
        """
        inp = arg.strip().lower()

        if inp == "":
            print("What do you want to read?")
            return False
        
        valid = self.find_valid(inp, self.current_room.objects + self.items)

        read = [x for x in valid if isinstance(x, Readable)]

        if len(read) == 0:
            print("Sorry, I cant read that")
        elif len(read) == 1:
            read[0].read(self)
        else:
            print(self.specific)


    def do_exit(self, arg=""):
        """
        Exit the game

        Usage: exit

        Dev Note: A save system has not been implemented yet
        """
        return True

    def do_unlock(self, args):
        """
        Attempts to unlock a door, requires you to have the correct key
        Usage: unlock <door name>

        Unless there are multiple doors in one room,
        "Unlock door" should work. 
        """
        
        inp = args.strip().lower()
        if inp == "":
            print("Sorry, an argument is needed, Try 'unlock door'")
            return False

        valid = self.find_valid(inp, self.current_room.objects)

        if len(valid) == 0:
            print(f"Sorry, I don't know what you mean by '{args}'")
            return False
        
        doors = [i for i in self.find_valid(inp, self.current_room.objects) if isinstance(i, Door)]

        if len(doors) == 0:
            print("Sorry I can't open that.")
            return False

        valid_keys = [i for i in self.items if isinstance(i, Key) and i.descriptor == doors[0].descriptor]

        if len(valid_keys) == 0:
            print(f"Sorry, You dont have the key to unlock the {doors[0].name}.")
            return False
        return self.do_use(valid_keys[0].name) # I want to have the unlock code in one(ish) place 

    def do_drop(self, arg):
        """
        Drop an Item in a room

        Usage: drop <Item>

        Dev Note: I don't know why you would use this since the inventory is infinite, 
            but I was advised to add this so...
        """
        inp = arg.strip().lower()
        valid = self.find_valid(inp, self.items)
        if len(valid) == 0:
            print(f"You don't have a '{arg}'.")
        elif len(valid) == 1:
            print(f"You dropped the {valid[0].name}")
            self.items.remove(valid[0])
            self.current_room.items.append(valid[0])
        else:
            print(self.specific)
    
    def do_inventory(self, arg):
        """
        Views your current inventory
        """
        if len(self.items) > 0:
            print(f"Items: {", ".join([i.name for i in self.items])}")
        else:
            print("You have no Items!")

    if DEBUG:
        def do_shell(self, arg):
            """
            For debugging use, executes command as python code

            Usage: !<Command>

            Dev Note: this does not print expressions by default like an IDLE so a print statement is usually needed
            Dev Note 2: Dont even try to write functions or anything that needs multiple lines here.
            """
            exec(arg, globals())
            return False

    ### --- Begin Alias --- ### 
    def do_EOF(self, arg):
        """
        an alias of exit for EOF support
        """
        return self.do_exit()

    def do_examine(self, arg):
        """
        Examines a room or Item
        """
        return self.do_look(arg)

    def do_open(self, arg):
        """ 
        Open a Door or Container
        Usage: open [door or container name]
        """
        valid = self.find_valid(arg.strip().lower(), self.current_room.objects)

        if len(valid) == 0:
            print(f"Sorry, I dont know what a '{arg}' is")
        elif len(valid) > 1:
            print(self.specific)
        elif isinstance(valid[0], Door):
            if isinstance(valid[0], Broken_Door):
                print("The door is broken!")
                return False
            self.do_unlock(valid[0].name)
        elif isinstance(valid[0], Container):
            self.current_room.items += valid[0].items
            for item in valid[0].items:
                print(f"You found a {item.name}")

            valid[0].items = []
            
            pass
        return False
        
        # Needs to open both Door and objects that hold items 

    ### --- Single Letter Alias --- ###
    def do_i(self, arg):
        """
        An alias of inventory
        see inventory help page for more information 
        """
        return self.do_inventory(arg)
    
    def do_n(self, arg):
        "An alias of 'go north'"
        return self.do_go("North")

    def do_e(self, arg):
        "An alias of 'go east'"
        return self.do_go("East")

    def do_s(self, arg):
        "An alias of 'go south"
        return self.do_go("South")

    def do_w(self, arg):
        "An alias of 'go west'"
        return self.do_go("West")

    




    


    def do_help(self, arg):
        """
        gets help
        """
        if arg.strip() == "":

            fun = [ i.lstrip("do").lstrip("_") for i in self.__class__.__dict__.keys() if i.startswith("do_")]
            print("Commands:")
            print(", ".join(fun))
        else: 
            if "do_" + arg.strip() in self.__class__.__dict__.keys():
                print(self.__class__.__dict__["do_" + arg.strip()].__doc__)
            else:
                print(f"Unkown Command {arg}")




    def emptyline(self):
        """
        Exists so pressing enter does not repeat last entered command
        """
        return False



class Room:
    """
    This class represents a room (duh)
    It has references to other rooms based on direction.

    The Room class has its own internal reference function so it should not be needed
        to to assign to a variable. instead use `Room.get([room name])` to get a reference 
        to a room, though the `Room.connect` method takes a room name and not the reference 
        to make writing all of the connections easier. (I will probably add support for directly
        giving a `Room` object later)

    Please be aware of the class methods, `Room.connect()` and `Room.get()` they do not need 
        to be called from a Room object and are designed to be called directly from `Room`
    """
    # TODO: write better docstring
    _rooms = {}



    def __init__(self, name: str, desc : str = "", items : Optional[list[Item]] = None, objects : Optional[list[Object]] = None):
        """
        Initalizes a room instance, does not need to be assigned to a variable

        name: The name of the room
        desc: The Rooms Description
        items: (Optional) A list of items in the room
        objects: (Optional) A list of objects in the room
        """
        self.desc = desc
        self.name = name
        self.items = items.copy() if items else []
        self.objects = objects.copy() if objects else []
        self._register(self)

        self.exits: dict[Direction, Room | None] = {"North": None, 
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
            raise ValueError(f"Direction {direction} is claimed in {self.name} and can't connect to {connection.name}")
        else:
            self.exits[direction] = connection


    @classmethod
    def connect(cls, room1: str, exit1: Direction, room2: str, exit2: Direction) -> None:
        """
        Connect 2 rooms together
        Arguments:
            room1: a string, the name of the first room you want to connect.
            exit1: a string/Direction. What exit from room1 will lead to room2?
            room2: a string, the name of the second room you want to connect.
            exit2: a string/Direction. What exit from room2 will lead to room1?
        """     

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
        
class Item(ABC):
    """
    The Item class is for things that the player can pick up.

    This should not be directly used but subclassed into specific items.

    There is currently a limitation that the player can only have one of an Item at a time
    (ok not really, but it would be multiple references to the same object)
    """
    items: dict[str, Item] = {}
    def __init__(self, name: str, desc: str):
        self.name = name
        self.desc = desc
        self._register(self)
        pass

    @abstractmethod
    def use(self, game: Game) -> None:
        """
        Whatever happens when you use this item,
        This should be overridden by a subclass
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
    


class Object(ABC):

    objects: dict[str, Object] = {}

    def __init__(self, name: str, desc: str):
        """
        An object exists so that that the player can interact with but not pickup and take, 
        can also be seen by items like keys

        Like `Items` this should not be used by itself but subclassed into a more specific object
        """
        self.name = name
        self.desc = desc
        self._register(self)

    @abstractmethod
    def use(self, game: Game) -> None:
        """
        Whatever happens when you use this object,
        This should be overridden by a subclass
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
            raise ValueError(f"Object, {object_name} does not exist!")

class Readable(ABC):
    """
    This class does not implement anything, its just here for filtering and readability
    This should be subclassed along with a instance of `Item` or `Object`
    """

    @abstractmethod
    def read(self, game: Game) -> None:
        """
        Read the Readable.
        needs to be implemented by subclass
        """
        return
    def use(self, game: Game) -> None:
        self.read(game)



### --- Sub Classes --- ###

class Door(Object):
    def __init__(self, name: str, desc: str, descriptor: str):
        self.locked = True
        self.descriptor = descriptor
        super().__init__(name, desc) 
        # IDEA: we might want to allow desc to be a function to dynamically change the description

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
        unlocks the door. normally called by a key
        """
        if not self.locked:
            print("The door is already unlocked!")
            return
        try:
            # This is so inefficient, ill prob fix this later to accept room objects
            Room.connect(self.room1.name, self.exit1, self.room2.name, self.exit2)
            # Guess what, I didnt fix this
        except AttributeError as e:
            print(e)
            print("Failed to initialize door connection and unlock door, in the future use door.connect to add to code!")
        self.locked = False
        print("[PLACEHOLDER] The door has unlocked!")
    @classmethod
    def get(cls, object_name: str) -> Door:
        result = super().get(object_name)
        if not isinstance(result, Door):
            raise ValueError("Doors can only get Doors!")

        return result



class Key(Item):
    def __init__(self, name: str, desc:str, descriptor: str):
        self.descriptor = descriptor
        super().__init__(name, desc)

    def use(self, game: Game, door: Door | None = None) -> None:
        # The Key use method is only called with a door when auto using the correct key,
        if door is not None:
            door.unlock()
        # Otherwise we need to see if we have a valid door
        else:
            doors: list[Door] = [d for d in game.current_room.objects if isinstance(d, Door)]
            for d in doors:
                if self.descriptor == d.descriptor and d.locked:
                    d.unlock()
                    game.items.remove(self) 
                    return
            print("There is nowhere to use that key here")


class Sign(Readable, Object):
    def __init__(self, name: str, desc: str, text: str):
        self.text = text
        super().__init__(name, desc)

    def read(self, game: Game):
        print(self.text)
        # TODO: show the text in a ASCII art sign

class Broken_Door(Door):
    def __init__(self, name: str, disc: str):

        super().__init__(name, disc, "BROKEN")
    def unlock(self) -> None:
        print("The lock on the door is broken!")
    def use(self, game: Game) -> None:
        print("The Door is Broken and you can't open it!")

class Container(Object):
    """
    A Mixin For objects that can hold items.
    """
    def __init__(self, name: str, disc: str, items: list[Item]):
            self.items = items.copy()
            super().__init__(name, disc)
    def use(self, game):
        print("Sorry you cant use this!")

class Shelf(Container):
    """
    Its a shelf... I dont know what you want me to say...
    """
    def __init__(self, name: str, disc: str, items: list[Item]):
        super().__init__(name, disc, items)

class Desk(Container):
    def __init__(self, name, disc, items):
        super().__init__(name, disc, items)

    def read(self, game):
        return super().read(game)

class Math_Homework(Item):
    def random_problem(self) -> tuple[int, int, str, int]:
        number_1 = randint(30, 80)
        number_2 = randint(1, number_1)
        result = None
        operator = choice(["+", "-", "*"])
        match operator:
            case "+":
                result = number_1 + number_2
            case "-":
                result = number_1 - number_2
            case "*":
                result = number_1 * number_2
            case _:
                raise RuntimeError(f"This should never happen, got {operator}")
        return number_1, number_2, operator, result

    def format_problem(self) -> tuple[str, int]:
        p = choice(["Solve_1", "Solve_2", "Result", "Result", "Result"]) # we want it to land on "Result" more than "Solve"
        n_1, n_2, operator, result = self.random_problem()
        problem: str = None
        ans: int = None 
        match p:
            case "Result":
                problem = f"{n_1} {operator} {n_2} = x"
                ans = result
            case "Solve_1":
                problem = f"x {operator} {n_2} = {result}"
                ans = n_1
            case "Solve_2":
                problem = f"{n_1} {operator} x = {result}"
                ans = n_2
        return problem, ans
    def use(self, game):
        # I know there are better ways to do this that are more "oop" like assigning the finish state to the HW instance,
        # But I think this works fine
        if game.flags["homework"]:
            print("You have already done your homework!")
            return
        problems = [self.format_problem() for i in range(6)]
        prompt = "HW> "
        print("You are beggining the homework minigame!")
        print("Please solve for x")
        exit = False
        for problem, answer in problems:
            loop = True
            print(problem)
            while loop and not exit:
                inp = input(prompt).strip().lower()
                if inp == "exit":
                    exit = True
                    break
                try:
                    answer_input = int(inp)
                except ValueError:
                    print("Sorry I cant turn that into a int")
                    continue
                if answer_input == answer:
                    print("Correct!")
                    # I know that the break should _theorecticly_ end the loop, but ive had bugs with the the break statement before
                    loop = False
                    break
                else:
                    print("Sorry Try again")

            if exit:
                break
        if not exit: # If the player actualy finished their HW
            game.flags["homework"] = True
    
        return

class Bed(Object):
    def __init__(self, name, desc):
        super().__init__(name, desc)


    def use(self, game):
        # Before sleeping we should check to make sure HW is done
        if not game.flags["homework"]:
            print("you should get your homework done before you go to bed!")
            return
        elif not game.flags["teeth"]:
            print("You should brush your teeth before going to bed!")
        else:
            print("You go to bed having done your Homework and gotten inside")
            print("This is the end of the story, Thanks for playing!")
            print("Type `exit` to exit or you can keep exploring!")

## -- Filler Objects -- ##

class Couch(Object):
    def use(self, game):
        print("You sit on the couch for a bit...")

class TV(Object):
    def __init__(self, name, desc):
        self.on = False
        super().__init__(name, desc)
    def use(self, game):
        if self.on:
            print("You turn of the TV")
        else:
            print("you turn on the TV")
        self.on = not self.on

class Toothbrush(Item):
    def use(self, game):
        if game.flags["teeth"]:
            print("You have already brushed your teeth")
            return
        if game.current_room is Room.get("Bathroom"):
            print("You brush your teeth")
            game.flags["teeth"] = True
        else:
            print("You should be in the Bathroom to brush your teeth!")
        return 

class Sink(Object):
    """
    its a sink for skink thinks (I ran out of things to add ok?)
    """
    def use(self, game):
        print("You wash your hands in the sink")

class Toilet(Object):
    """
    at this point im just adding random things
    its filler ok?
    """
    def use(self, game):
        print("You use the Toilet (and flush)")

class Oven(Object):
    def use(self, game):
        print("Its a oven, you dont want to turn it on if you have nothing to cook")

class Carrot(Item):
    def use(self, game):
        print("You eat the Carrot")
        game.items.remove(self)
    
class Painting(Object):
    def use(self, game):
        print("You stare at the painting for a bit")

## --- Time to start creating all of the objects --- ##

# - Items - #

#Keys
Key("House Key", "The Key to your House.", "House")
Key("Garden Key", "The Key to your Garden", "Garden")

#Homework
Math_Homework("Math Homework", "Math Homework, You Really Should Get this done")

# - Objects - #


#Doors
Door("Garden Gate", "The Gate To the Garden is Locked", "Garden")
Door("House Door", "The Door to your House", "House")
Broken_Door("Backdoor", "The backdoor to your house, its sadly broken")

#Signs
Sign("Introduction Sign", 
     "A Oak sign that welcomes you to this world and helps guide you in your journey", 
"""Welcome to my Text Adventure game!
In this game there are no visuals, only text and commands
To move around type `go [direction]`
The valid directions are: North West East South (The first 
Initial is also accepted)
To use an item type `use [item]` 
To look at an item type `look <item>`
Without arguments It shows the room description and the
valid movement directions
Try it Now!""")

#Desk
Desk("Your Desk", "Its your desk", items=[Item.get("Math Homework")])

#Filler
TV("TV", "Your TV")
Couch("Couch", "Your Couch")
Bed("Bed", "Your Bed")

Sink("Bathroom Sink", "Its the sink for the bathroom")
Sink("Kitchen Sink", "Its the sink for the kitchen")
Carrot("Carrot", "Its a carrot you grew yourself in the Garden")
Oven("Oven", "Its your oven...")
Toilet("Toilet", "Its a Toilet...")
Toothbrush("Toothbrush", "A Green Electric Toothbrush")
Painting("Painting", "A painting of a boat on a river at night in the moonlight")
Painting("Art", "Some hand drawn art that you drew when you where little")


# Need to come up with a good name
Shelf("Misc Shelf", "You bought an extra shelf and it has been the home for a lot of random things", [Item.get("Garden Key")])

### ---  Rooms --- ###

Room("Start", "The start of the game", objects=[Object.get("Introduction Sign")])
Room("Lawn", "There is green grass all around you")
Room("Front Porch", "you are not inside the building yet..")
Room("Side of House", "The side of your house")
Room("Garden", "Your garden, There are a bunch of plants growing here", items=[Item.get("House Key"), Item.get("Carrot")])
Room("Back of House", "The back of your house", objects=[Object.get("Backdoor"), Object.get("Misc Shelf")])
Room("House Entrance", "The first room in your house")
Room("Living Room", "A comfortable living room with a couch and a large window", objects=[Object.get("TV"), Object.get("Couch")])
Room("Kitchen", "The kitchen is tidy, with counters along the walls and a small table", objects=[Object.get("Kitchen Sink"), Object.get("Oven"), Object.get("Art")])
Room("Hallway", "A narrow hallway leads deeper into the house", objects=[Object.get("Painting")])
Room("Bathroom", "A small bathroom with a mirror above the sink", objects=[Object.get("Bathroom Sink"), Object.get("Toilet")], items=[Item.get("Toothbrush")])
Room("Bedroom", "Your bedroom, with a bed and a desk covered in homework", objects=[Object.get("Your Desk"), Object.get("Bed")])
## --- Connecting objects to eachother --- ##

# Outside Rooms
Room.connect("Start", "North", "Lawn", "South")
Room.connect("Lawn", "West", "Front Porch", "East")
Room.connect("Front Porch", "South", "Side of House", "East")
Room.connect("Side of House", "West", "Back of House", "East")

# House interior (USED AI TO HELP MAKE LAYOUT)
Room.connect("House Entrance", "West", "Living Room", "East")
Room.connect("Living Room", "North", "Kitchen", "South")
Room.connect("Living Room", "West", "Hallway", "East")
Room.connect("Hallway", "North", "Bathroom", "South")
Room.connect("Hallway", "West", "Bedroom", "East")




# Doors
Door.get("House Door").connect("Front Porch", "West", "House Entrance", "East")
Door.get("Garden Gate").connect("Front Porch", "North", "Garden", "South")


if __name__ == "__main__":
    game = Game(Room.get("Start"))
    game.cmdloop()