import json
import random
import time

# A game without good features is not worth playing, so I added some simple features to the standard game like menu and colors

# I used camelCase for my all functions, snake_case for my all variables, and PascalCase for my all classes
# I marked empty fields with colors instead of E char in order to prevent clutter
# I used mutable types all over my program since they could be used as references on function calls
# Also I used ANSI escape codes all over my game

class Player:
    '''Takes a name and instantiates a Player object
    
    A Player object holds instant data about the player as the name suggests
    '''
    # Initial values for a player
    alive = True
    score = 0
    sword_count = 0
    potion_count = 0

    def __init__(self, name=None):
        self.name = name or "Anonymous"

class Map:
    # Because this way seems simpler, I didn't choose to represent my map as a multidimensional list or something like that
    width, height = 7, 6

    # I can't explain, but these made my job easier
    # Reference for player's location
    def _get_player_location(self):
        return self.locations[0]
    
    def _set_player_location(self, location):
        self.locations[0] = location

    player_location = property(fget=_get_player_location, fset=_set_player_location)

    def __init__(self, settings, example=False):
        # Create a map which seems like empty at the beginning of a game session
        # False stands for unvisited while True stands for visited
        self.tiles = [False for _ in range(self.width * self.height)]
        self.settings = settings

        if example == False:
            # Determine the locations of entities
            # U stands for user
            # Map keeps player's location since it uses it to draw
            self.entities = 1 * "U" + 5 * "M" + 3 * "V" + 5 * "T" + 2 * "S" + 3 * "P"
            self.locations = random.sample(range(self.width * self.height), len(self.entities))

            # Mark the initial location
            self.tiles[self.player_location] = True
        else:
            self.entities = "U"
            self.locations = [32]
            self.tiles[32] = True
            for tile in (25, 24, 23, 16):
                self.tiles[tile] = True

    def __getitem__(self, index):
        return self.tiles[index]

    # Map represantation
    # That's a bit complex
    # It would be simpler if I didn't use colors on my map, MUCH MUCH SIMPLER
    def __str__(self):
        self.map_list = []

        for line in range(self.height):
            self.map_list.append("[")
            for column in range(self.width):
                position = 7 * line + column
                revealed = self.settings["entities"] + f"'{self.get(position)}'" + self.settings["default"] if position in self.locations else self.settings["revealed_tiles"] + "' '" + self.settings["default"]
                self.map_list.append(revealed if self[position] else "' '")
                self.map_list.append("" if column == self.width - 1 else ", ")
            self.map_list.append("]" + ("\n" if line != self.width - 1 else ""))
        
        return self.settings["default"] + "".join(self.map_list)

    # This one is more performant but I used the __str__ function instead of this
    def write(self):
        print(self.settings["default"], end="")
        for line in range(self.height):
            print("[", end="")
            for column in range(self.width):
                position = 7 * line + column
                revealed = self.settings["entities"] + f"'{self.get(position)}'" + self.settings["default"] if position in self.locations else self.settings["revealed_tiles"] + "' '" + self.settings["default"]
                print(revealed if self[position] else "' '", end=("" if column == self.width - 1 else ", "))
            print("]")
    

    def get(self, position, *, start_from=0):
        try:
            return self.entities[self.locations.index(position, start_from)]
        except IndexError:
            return None
        except ValueError:
            return None

    # Mark the visited tiles
    def mark(self, location):
        self.tiles[location] = True

class Logger:
    '''A simple logger'''

    def __init__(self, player):
        self.player = player
        self.moves = []

    def move(self, direction):
        self.moves.append(direction)

    # Load log into ram in order to use it for appending
    def load_log(self):
        try:
            with open("gamelog.json", "x") as f:
                pass
        except FileExistsError:
            try:
                with open("gamelog.json") as log_file:
                    return json.load(log_file)
            except json.JSONDecodeError:
                return {}
        else:
            return {}

    # Log the latest game
    def log(self):
        # log_obj is the last game which is about to be appended to our log_dict
        log_obj = {"moves": self.moves, "score": self.player.score}

        # Append the log_obj to the other logs
        log_dict = self.load_log()
        log_dict[time.strftime("%d/%m/%Y %H:%M:%S")] = log_obj

        with open("gamelog.json", "w") as log_file:
            json.dump(log_dict, log_file, indent=4)

def rgbRepr(color):
    '''Gets color as a string or a list and converts it to the other format'''
    if isinstance(color, str):
        return color.removeprefix("\033").removeprefix("[38;2;").removesuffix("m").split(";")
    else:
        return f"\033[38;2;{color[0]};{color[1]};{color[2]}m"

def setSettings(settings):
    temporary_map = Map(settings, example=True)

    while True:
        # Print example game screen
        print("\033[H\033[J", end="")
        print(temporary_map, end="")
        print("\n---------------------\n")
        print(settings["event"], "EXTRA INFO(Event)", settings["default"], sep="")
        print("\n---------------------\n")
        print(settings["player_state"], "Player: ", "Anonymous", "  Score: ", 0, "  Sword: ", 0, "  Potion: ", 0, settings["default"], sep="", end="\n\n")
        print("You can set color for: ")
        print("\t1. Default: ", rgbRepr(settings["default"]))
        print(settings["entities"], "\t2. Entities: ", rgbRepr(settings["entities"]), sep="")
        print(settings["player_state"], "\t3. Player State: ", rgbRepr(settings["player_state"]), sep="")
        print(settings["revealed_tiles"], "\t4. Revealed Tiles: ", rgbRepr(settings["revealed_tiles"]), sep="")
        print(settings["event"], "\t5. Event: ", rgbRepr(settings["event"]), settings["default"], sep="")
        print("Writing something else will turn you back to main menu")

        # Get the option which player has chosen in order to use it for changing that option
        while (option := input("What do you want to set: ")) not in "12345" or option == "":
            return None
        
        # Get the color from user for the option
        while len(color := list(map(int, input("Write your color at decimal rgb format separated by spaces: ").split()))) != 3 or not all(map(lambda x: 0 <= x <= 255, color)):
            print("\033[1F\033[2KYou should write 3 decimal numbers in range [0, 255], try again! ", end="")
        
        if option == "1":
            settings["default"] = rgbRepr(color)
        elif option == "2":
            settings["entities"] = rgbRepr(color)
        elif option == "3":
            settings["player_state"] = rgbRepr(color)
        elif option == "4":
            settings["revealed_tiles"] = rgbRepr(color)
        elif option == "5":
            settings["event"] = rgbRepr(color)
        else:
            return None


def update(logr, game_map, player, available_sides):
    # Wait for user to input 1 character
    user_input = input("Press L, U, R, D to move: ").lower()

    # Correct the user input
    while len(user_input) != 1 or user_input not in "lurd" or user_input not in available_sides:
        user_input = input("\033[1F\033[2KI'm sorry this is not possible, try again: ").lower()

    # Send user input to logger
    logr.move(user_input)
    
    # Set the values by using user input
    if user_input == "l":
        game_map.player_location -= 1
    elif user_input == "u":
        game_map.player_location -= game_map.width
    elif user_input == "r":
        game_map.player_location += 1
    elif user_input == "d":
        game_map.player_location += game_map.width

    game_map.mark(game_map.player_location)
    tile_content = game_map.get(game_map.player_location, start_from=1)
    if tile_content is None:
        pass
    elif tile_content == "T":
        player.score += 1
    elif tile_content == "S":
        player.sword_count += 1
    elif tile_content == "P":
        player.potion_count += 1
    elif tile_content == "M":
        if player.sword_count != 0:
            player.sword_count -= 1
        else:
            player.alive = False
    elif tile_content == "V":
        if player.potion_count != 0:
            player.potion_count -= 1
        else:
            player.alive = False
    
    if player.alive:
        player.score += 1

    return tile_content
    

def draw(game_map, player, tile_content, settings):
    # Clear the screen
    print("\033[H\033[J", end="")

    # Draw map
    print(game_map, end="")

    # Print extra information
    if tile_content is not None:
        print("\n---------------------\n" + settings["event"])
        if tile_content == "T":
            print("+TREASURE")
        elif tile_content == "S":
            print("+SWORD")
        elif tile_content == "P":
            print("POTION")
        elif tile_content == "M":
            print("Oh No! MONSTER.")
            if player.alive:
                print("SWORD is used.")
            else:
                print("You die.")
        elif tile_content == "V":
            print("Oh No! VENOM.")
            if player.alive:
                print("POTION is used.")
            else:
                print("You die.")
    print(settings["default"] + "\n---------------------\n")
    print(settings["player_state"], "Player: ", player.name, "  Score: ", player.score, "  Sword: ", player.sword_count, "  Potion: ", player.potion_count, settings["default"], sep="", end="\n\n")

def gameLoop(settings):
    # Create a random Map
    game_map = Map(settings)
    
    # Create a Player
    print("You are not forced to give a name.")
    player = Player(input("What is your name: "))

    # Initialize Logger
    logr = Logger(player)

    # I used this to store tile content in game loop
    tile_content = None

    # Main game loop
    while True:
        # Draw map and print extra information
        draw(game_map, player, tile_content, settings)

        # Check if player is dead or alive
        # I checked it here instead of inside while statement because draw must run after player dies
        if not player.alive:
            print("\033[1;31mGame over!\033[22m" + settings["default"])
            input("Press enter in order to return to main menu")
            break

        # Check which sides player can move
        directions = {"l", "u", "r", "d"}
        player_y, player_x = divmod(game_map.player_location, game_map.width)

        adjacent_borders = set()
        if player_x == 0:
            adjacent_borders.add("l")
        elif player_x == game_map.width - 1:
            adjacent_borders.add("r")

        if player_y == 0:
            adjacent_borders.add("u")
        elif player_y == game_map.height - 1:
            adjacent_borders.add("d")
        
        occupied_adjacent_tiles = set()
        if "l" not in adjacent_borders and game_map[game_map.player_location - 1]:
            occupied_adjacent_tiles.add("l")
        if "r" not in adjacent_borders and game_map[game_map.player_location + 1]:
            occupied_adjacent_tiles.add("r")
        if "u" not in adjacent_borders and game_map[game_map.player_location - 7]:
            occupied_adjacent_tiles.add("u")
        if "d" not in adjacent_borders and game_map[game_map.player_location + 7]:
            occupied_adjacent_tiles.add("d")

        available_sides = directions - adjacent_borders - occupied_adjacent_tiles

        # I was going to put this and previous code blocks into update function, but I decided it would be shorter this way
        # If player got stuck, finish the game session
        if len(available_sides) == 0:
            print("\033[1;31mGame over!\033[22m" + settings["default"])
            input("Press enter in order to return to main menu")
            break

        # Update values by using user input, and store any information that update function can return
        tile_content = update(logr, game_map, player, available_sides)
    
    # Log the finished game
    logr.log()

def menu():
    # Every time you restart the program settings will be set to these default values
    # Actually settings are colors
    settings = {"default": rgbRepr([191, 213, 201]), "entities": rgbRepr([0, 99, 115]), "player_state": rgbRepr([5, 163, 164]), "revealed_tiles": rgbRepr([179, 90, 32]), "event": rgbRepr([232, 137, 29])}

    # Set default color
    print(settings["default"])

    # I created options list in order to use it within print function
    options = ["Play", "Settings", "Exit"]

    while True:
        # Clear screen before and after everything
        print("\033[H\033[J", end="")

        # Print the options
        print(*[f"{option}: {index + 1}" for index, option in enumerate(options)], sep="\n")

        # Get the user's choice, and clear screen
        while len(chosen_option := input("Choose an option: ")) == 0 or chosen_option not in ["1", "2", "3"]:
            print("\033[1F\033[2KThat is not an option, try again! ", end="")
        chosen_option = int(chosen_option)
        print("\033[H\033[J", end="")
        
        # Evaluate the user's choice, and use it to maintain the program's flow
        if chosen_option == 1:
            # Start a game session
            gameLoop(settings)
        elif chosen_option == 2:
            # Show settings screen
            setSettings(settings)
        elif chosen_option == 3:
            # Exit the game
            break
        else:
            print("How did you achieve this?!")
            input()
            break

menu()