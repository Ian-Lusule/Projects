```python
import random
import time

class Room:
    def __init__(self, name, description, items=None, exits=None):
        self.name = name
        self.description = description
        self.items = items if items is not None else []
        self.exits = exits if exits is not None else {}  # {direction: Room}

    def __str__(self):
        return f"{self.name}\n{self.description}\nExits: {', '.join(self.exits.keys()) or 'None'}\nItems: {', '.join(self.items) or 'None'}"

class Player:
    def __init__(self, name, current_room):
        self.name = name
        self.inventory = []
        self.current_room = current_room
        self.health = 100
        self.attack = 10

    def move(self, direction):
        if direction in self.current_room.exits:
            self.current_room = self.current_room.exits[direction]
            print(f"You moved {direction} to {self.current_room.name}")
            self.current_room.on_enter(self)
        else:
            print("You can't go that way!")

    def take_item(self, item_name):
        if item_name in self.current_room.items:
            self.inventory.append(item_name)
            self.current_room.items.remove(item_name)
            print(f"You picked up {item_name}")
        else:
            print(f"There's no {item_name} here.")

    def drop_item(self, item_name):
        if item_name in self.inventory:
            self.inventory.remove(item_name)
            self.current_room.items.append(item_name)
            print(f"You dropped {item_name}")
        else:
            print(f"You don't have {item_name}.")

    def attack_enemy(self,enemy):
        damage = random.randint(self.attack -3, self.attack + 3)
        enemy.health -= damage
        print(f"You attacked the {enemy.name} for {damage} damage!")
        if enemy.health <= 0:
            print(f"You defeated the {enemy.name}!")
            self.current_room.enemies.remove(enemy)
        else:
            print(f"The {enemy.name} has {enemy.health} health remaining.")

    def use_item(self, item_name):
        if item_name in self.inventory:
            if item_name == "potion":
                self.health = min(100, self.health + 20)
                self.inventory.remove(item_name)
                print("You drank the potion and restored 20 health!")
            else:
                print(f"You don't know how to use {item_name}.")
        else:
            print(f"You don't have {item_name}.")

class Enemy:
    def __init__(self, name, health, attack):
        self.name = name
        self.health = health
        self.attack = attack

    def attack_player(self, player):
        damage = random.randint(self.attack - 3, self.attack + 3)
        player.health -= damage
        print(f"The {self.name} attacked you for {damage} damage!")


def create_game():
    # Create rooms
    entrance = Room("Entrance Hall", "A grand entrance hall with a large oak door to the north and a winding staircase to the east.", exits={"north":north_hall, "east":staircase})
    north_hall = Room("North Hall", "A long, dimly lit hallway. A flickering torch reveals a passage to the west.", exits={"west":entrance})
    staircase = Room("Staircase", "A winding staircase leading up to the second floor.", exits={"down":entrance})
    
    #add items and enemies
    entrance.items = ["key"]
    north_hall.enemies = [Enemy("Goblin", 20, 5)]


    # Create player
    player = Player("Hero", entrance)

    return player

def game_loop(player):
    while player.health > 0:
        print("\n"+str(player.current_room))
        print(f"Inventory: {', '.join(player.inventory) or 'None'}")
        print(f"Health: {player.health}")

        command = input("> ").lower().split()
        verb = command[0]

        if verb == "go" or verb == "move":
            if len(command) > 1:
                direction = command[1]
                player.move(direction)
            else:
                print("Go where?")

        elif verb == "take":
            if len(command) > 1:
                item_name = command[1]
                player.take_item(item_name)
            else:
                print("Take what?")

        elif verb == "drop":
            if len(command) > 1:
                item_name = command[1]
                player.drop_item(item_name)
            else:
                print("Drop what?")

        elif verb == "attack":
            if len(command) > 1:
                enemy_name = command[1]
                for enemy in player.current_room.enemies:
                    if enemy.name.lower() == enemy_name:
                        player.attack_enemy(enemy)
                        if enemy.health > 0:
                            enemy.attack_player(player)
                        break
                else:
                    print(f"There is no {enemy_name} here.")
            else:
                print("Attack what?")

        elif verb == "use":
            if len(command) > 1:
                item_name = command[1]
                player.use_item(item_name)
            else:
                print("Use what?")

        elif verb == "quit":
            break

        elif verb == "help":
            print("Available commands: go/move, take, drop, attack, use, quit, help")
        else:
            print("I don't understand that command.")
            
        time.sleep(1)

    if player.health <= 0:
        print("You have been defeated!")


# Start the game
player = create_game()
game_loop(player)

```