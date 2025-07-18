import pygame
import random
import time
import pickle
import socket
import threading
import sys
import os
import math

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Advanced Pygame Game")

# Clock for controlling FPS
clock = pygame.time.Clock()

# Font
font = pygame.font.Font(None, 36)

# --- Helper Functions ---
def load_image(filename, colorkey=None):
    try:
        image = pygame.image.load(filename).convert()
    except pygame.error as message:
        print('Cannot load image:', filename)
        raise SystemExit(message)
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey)
    return image

def load_sound(name):
    class NoneSound:
        def play(self): pass
    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()
    try:
        sound = pygame.mixer.Sound(name)
    except pygame.error as message:
        print('Cannot load sound:', name)
        raise SystemExit(message)
    return sound

def save_game(data, filename="savegame.dat"):
    try:
        with open(filename, "wb") as file:
            pickle.dump(data, file)
        print("Game saved!")
    except Exception as e:
        print("Error saving game:", e)

def load_game(filename="savegame.dat"):
    try:
        with open(filename, "rb") as file:
            data = pickle.load(file)
        print("Game loaded!")
        return data
    except FileNotFoundError:
        print("Save file not found.")
        return None
    except Exception as e:
        print("Error loading game:", e)
        return None

def generate_level(level_num):
    # Procedurally generate level data.  Can be significantly more complex.
    level_data = []
    num_blocks = 10 + level_num * 2
    for _ in range(num_blocks):
        x = random.randint(100, WIDTH - 100)
        y = random.randint(100, HEIGHT - 100)
        width = random.randint(50, 100)
        height = random.randint(20, 50)
        level_data.append((x, y, width, height))
    return level_data

# --- Game Classes ---

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, speed=5):
        super().__init__()
        self.image = pygame.Surface([32, 32])
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = speed
        self.health = 100
        self.score = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed

        # Keep player within bounds
        self.rect.x = max(0, min(self.rect.x, WIDTH - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, HEIGHT - self.rect.height))

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            return True # Indicate death
        return False

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, speed=2):
        super().__init__()
        self.image = pygame.Surface([32, 32])
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = speed
        self.ai = None # Placeholder for AI agent

    def update(self, player):
        # Simple AI: Chase the player
        if self.ai:
            # Use AI agent to determine movement
            action = self.ai.predict(self.get_state(player))
            if action == 0:  # Move left
                self.rect.x -= self.speed
            elif action == 1: # Move right
                self.rect.x += self.speed
            elif action == 2: # Move up
                self.rect.y -= self.speed
            elif action == 3: # Move down
                self.rect.y += self.speed

        else:
            dx = player.rect.x - self.rect.x
            dy = player.rect.y - self.rect.y
            dist = math.sqrt(dx**2 + dy**2)

            if dist > 0:
                dx /= dist
                dy /= dist

                self.rect.x += dx * self.speed
                self.rect.y += dy * self.speed

    def get_state(self, player):
        # Define state for the AI.  This needs to be carefully crafted.
        return (self.rect.x, self.rect.y, player.rect.x, player.rect.y)

    def set_ai(self, ai_agent):
        self.ai = ai_agent


class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, type):
        super().__init__()
        self.image = pygame.Surface([20, 20])
        self.image.fill(WHITE)  # Change color based on type later
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.type = type

    def apply(self, player):
        if self.type == "health":
            player.health = min(100, player.health + 20)
        elif self.type == "speed":
            player.speed += 2
            pygame.time.set_timer(pygame.USEREVENT + 1, 5000) # Speed boost lasts 5 seconds

# --- Game Functions ---

def handle_collision(player, group):
    collisions = pygame.sprite.spritecollide(player, group, False)
    if collisions:
        for block in collisions:
            # Simple collision resolution (can be improved)
            if player.rect.centerx < block.rect.left:
                player.rect.right = block.rect.left
            elif player.rect.centerx > block.rect.right:
                player.rect.left = block.rect.right
            if player.rect.centery < block.rect.top:
                player.rect.bottom = block.rect.top
            elif player.rect.centery > block.rect.bottom:
                player.rect.top = block.rect.bottom


# --- Network ---
def server_thread(host, port, game_state):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(2)  # Allow 2 connections (assuming 2 players)
    print(f"Server listening on {host}:{port}")

    connections = []
    while len(connections) < 2:
        conn, addr = server_socket.accept()
        print(f"Connected by {addr}")
        connections.append(conn)
        conn.send(b"Connected to server") # Send initial connection confirmation

    # Exchange initial game state
    try:
        # Send initial state to both clients
        data = pickle.dumps(game_state)
        for conn in connections:
            conn.sendall(data)


        while True:
            for conn in connections:
                try:
                    data = conn.recv(4096) # Adjust buffer size if needed
                    if not data:
                        print("Client disconnected")
                        connections.remove(conn)
                        break  # Exit inner loop if a client disconnects
                    try:
                        # Attempt to unpickle the data
                        received_state = pickle.loads(data)
                        # Update the game state based on received data (player positions, etc.)
                        game_state = received_state
                        # Relay the updated game state to the other client
                        other_conn = connections[1 - connections.index(conn)]
                        other_conn.sendall(pickle.dumps(game_state))

                    except pickle.UnpicklingError as e:
                        print(f"Unpickling error: {e}")
                        continue  # Skip to the next iteration if there's an error

                except socket.error as e:
                    print(f"Socket error: {e}")
                    connections.remove(conn)
                    break  # Exit inner loop if a socket error occurs

            if len(connections) < 2:
                break

    except Exception as e:
        print(f"Server error: {e}")

    finally:
        for conn in connections:
            conn.close()
        server_socket.close()
        print("Server closed.")


def client_thread(host, port, player_id, game_state, update_func):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((host, port))
        print(f"Connected to server at {host}:{port}")

        # Receive initial confirmation
        confirmation = client_socket.recv(1024).decode()
        print(confirmation)

        # Receive initial game state
        data = client_socket.recv(4096)
        initial_state = pickle.loads(data)
        game_state.update(initial_state)
        update_func(game_state) # Call the update function to apply the initial state

        while True:
            # Send player's updated state
            player_data = {f"player_{player_id}_x":game_state[f"player_{player_id}_x"],
                           f"player_{player_id}_y":game_state[f"player_{player_id}_y"]}
            data = pickle.dumps(player_data)

            client_socket.sendall(data)

            # Receive updated game state from server
            data = client_socket.recv(4096)
            if not data:
                print("Server disconnected.")
                break

            try:
                 received_state = pickle.loads(data)
                 game_state.update(received_state)
                 update_func(game_state) # Update local game state
            except pickle.UnpicklingError as e:
                 print(f"Unpickling error: {e}")
                 continue


    except socket.error as e:
        print(f"Socket error: {e}")

    finally:
        client_socket.close()
        print("Client disconnected.")



# --- Machine Learning (Basic Example - needs much improvement) ---
class SimpleAI:
    def __init__(self):
        self.q_table = {} # State -> Action values.  Needs to be persisted if training is desired.
        self.learning_rate = 0.1
        self.discount_factor = 0.9
        self.epsilon = 0.2  # Exploration rate

    def get_q_value(self, state, action):
        if (state, action) not in self.q_table:
            self.q_table[(state, action)] = 0.0
        return self.q_table[(state, action)]

    def choose_action(self, state):
        if random.random() < self.epsilon:
            return random.randint(0, 3)  # Explore: Choose a random action
        else:
            # Exploit: Choose the action with the highest Q-value
            q_values = [self.get_q_value(state, a) for a in range(4)]
            return q_values.index(max(q_values))

    def predict(self, state):
        # Simply choose best action based on current q-table.
        return self.choose_action(state)

    def learn(self, state, action, reward, next_state):
        # Q-learning update rule
        best_next_action = self.choose_action(next_state)
        best_next_q_value = self.get_q_value(next_state, best_next_action)
        old_q_value = self.get_q_value(state, action)
        new_q_value = old_q_value + self.learning_rate * (
                reward + self.discount_factor * best_next_q_value - old_q_value)
        self.q_table[(state, action)] = new_q_value
    def train(self, episodes, env, player, enemy): # 'env' would need to abstract game state.  Simplified example.
         for episode in range(episodes):
            state = enemy.get_state(player)
            done = False
            while not done:
                action = self.choose_action(state)
                # Simulate action and get reward (This needs to be game-specific)
                # This is where the environment comes in.
                # Example:
                if action == 0: #Left
                    enemy.rect.x -= enemy.speed
                elif action == 1:
                    enemy.rect.x += enemy.speed
                elif action == 2:
                    enemy.rect.y -= enemy.speed
                else:
                    enemy.rect.y += enemy.speed

                if enemy.rect.colliderect(player.rect):
                    reward = -10  # Collision is bad
                    done = True
                else:
                    reward = -1  # Small penalty for each step

                next_state = enemy.get_state(player)
                self.learn(state, action, reward, next_state)
                state = next_state



# --- Game States ---
class GameState:
    MENU = 0
    PLAYING = 1
    PAUSED = 2
    GAME_OVER = 3

# --- Main Game ---
def main():
    # Game variables
    game_state = GameState.MENU
    player = Player(WIDTH // 2, HEIGHT // 2)
    player_group = pygame.sprite.Group(player)
    enemies = pygame.sprite.Group()
    blocks = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    level = 1
    score = 0
    player_health = player.health

    # Networking
    is_multiplayer = False
    is_server = False
    server_thread_instance = None
    client_thread_instance = None
    network_game_state = {}
    player_id = 1  # Default, overwritten if client
    server_address = "127.0.0.1"  # Localhost by default
    server_port = 12345

    # AI
    ai_agent = SimpleAI()

    # Sound
    pygame.mixer.music.load("background.ogg") # Replace with your actual filename
    pygame.mixer.music.play(-1)  # Play indefinitely
    powerup_sound = load_sound("powerup.wav") # Replace with your actual filename
    damage_sound = load_sound("damage.wav") # Replace with your actual filename

    def start_new_game():
        nonlocal game_state, player, enemies, blocks, powerups, level, score, player_health, network_game_state

        # Reset all game-related variables
        player = Player(WIDTH // 2, HEIGHT // 2)
        player_group = pygame.sprite.Group(player)
        enemies = pygame.sprite.Group()
        blocks = pygame.sprite.Group()
        powerups = pygame.sprite.Group()
        level = 1
        score = 0
        player_health = player.health

        # Generate the first level
        level_data = generate_level(level)
        for x, y, width, height in level_data:
            block = Block(x, y, width, height)
            blocks.add(block)

        # Create an initial enemy
        enemy = Enemy(random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100))
        enemy.set_ai(ai_agent)
        enemies.add(enemy)


        # If in multiplayer, update network game state and start the server/client
        if is_multiplayer:
            network_game_state = {"player_1_x": player.rect.x, "player_1_y": player.rect.y,
                                  "player_2_x": WIDTH // 4, "player_2_y": HEIGHT // 4, # Initial position of player 2
                                  "enemy_x": enemy.rect.x, "enemy_y": enemy.rect.y,
                                  "score": 0}

            if is_server:
                 nonlocal server_thread_instance
                 server_thread_instance = threading.Thread(target=server_thread, args=(server_address, server_port, network_game_state))
                 server_thread_instance.daemon = True
                 server_thread_instance.start()
                 player_id = 1
            else:
                 nonlocal client_thread_instance
                 client_thread_instance = threading.Thread(target=client_thread, args=(server_address, server_port, 2, network_game_state, update_networked_game_state))
                 client_thread_instance.daemon = True
                 client_thread_instance.start()
                 player_id = 2

        game_state = GameState.PLAYING


    def update_networked_game_state(new_state):
        nonlocal player
        if player_id == 1:
            player.rect.x = new_state.get("player_1_x", player.rect.x)
            player.rect.y = new_state.get("player_1_y", player.rect.y)
        else:
             player.rect.x = new_state.get("player_2_x", player.rect.x)
             player.rect.y = new_state.get("player_2_y", player.rect.y)

    # Game loop
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if game_state == GameState.MENU:
                    if event.key == pygame.K_1:
                        is_multiplayer = False
                        start_new_game()
                    if event.key == pygame.K_2: #Multiplayer Menu
                        game_state = 4 # Multiplayer Menu
                    if event.key == pygame.K_l:
                        loaded_data = load_game()
                        if loaded_data:
                            player.rect.x = loaded_data['player_x']
                            player.rect.y = loaded_data['player_y']
                            level = loaded_data['level']
                            score = loaded_data['score']
                            player_health = loaded_data['health']
                            blocks.empty()
                            level_data = generate_level(level)  # Regenerate blocks
                            for x, y, width, height in level_data:
                                block = Block(x, y, width, height)
                                blocks.add(block)

                            game_state = GameState.PLAYING
                elif game_state == GameState.PLAYING:
                    if event.key == pygame.K_p:
                        game_state = GameState.PAUSED
                    if event.key == pygame.K_SPACE: # Example Power-Up spawn
                        powerup = PowerUp(random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50), "health")
                        powerups.add(powerup)

                elif game_state == GameState.PAUSED:
                    if event.key == pygame.K_p:
                        game_state = GameState.PLAYING
                    if event.key == pygame.K_s:
                        save_data = {'player_x': player.rect.x, 'player_y': player.rect.y,
                                     'level': level, 'score': score, 'health':player_health}
                        save_game(save_data)
                        game_state = GameState.MENU
                elif game_state == GameState.GAME_OVER:
                    if event.key == pygame.K_r: # Restart
                        start_new_game()
                    if event.key == pygame.K_m:
                        game_state = GameState.MENU
                elif game_state == 4: #Multiplayer Menu
                    if event.key == pygame.K_1:
                        is_multiplayer = True
                        is_server = True
                        start_new_game()
                    if event.key == pygame.K_2:
                        is_multiplayer = True
                        is_server = False
                        start_new_game()
                    if event.key == pygame.K_BACKSPACE: #Return to main Menu
                        game_state = GameState.MENU

            if event.type == pygame.USEREVENT + 1:
                player.speed = 5  # Reset speed after power-up duration

        # --- Game Logic ---
        if game_state == GameState.PLAYING:
            player.update()
            for enemy in enemies:
                enemy.update(player)

            handle_collision(player, blocks)
            for enemy in enemies:
                handle_collision(enemy, blocks)

            # Power-up collision
            powerup_collisions = pygame.sprite.spritecollide(player, powerups, True)
            for powerup in powerup_collisions:
                powerup.apply(player)
                powerup_sound.play()

            # Enemy collision
            enemy_collisions = pygame.sprite.spritecollide(player, enemies, False)
            if enemy_collisions:
                damage_sound.play()
                if player.take_damage(10):
                    game_state = GameState.GAME_OVER  # Player died
            #Level progression
            if len(enemies) == 0:
                level += 1
                score += 50
                level_data = generate_level(level)
                blocks.empty()
                for x, y, width, height in level_data:
                    block = Block(x, y, width, height)
                    blocks.add(block)

                enemy = Enemy(random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100))
                enemy.set_ai(ai_agent)
                enemies.add(enemy)
            if is_multiplayer:
                #Update server with player and enemy state
                network_game_state["player_1_x"] = player.rect.x if player_id == 1 else network_game_state.get("player_1_x", 0)
                network_game_state["player_1_y"] = player.rect.y if player_id == 1 else network_game_state.get("player_1_y", 0)
                network_game_state["player_2_x"] = player.rect.x if player_id == 2 else network_game_state.get("player_2_x", 0)
                network_game_state["player_2_y"] = player.rect.y if player_id == 2 else network_game_state.get("player_2_y", 0)
                network_game_state["enemy_x"] = enemy.rect.x
                network_game_state["enemy_y"] = enemy.rect.y

            score += 1  # Score increases over time
            player_health = player.health


        # --- Drawing ---
        screen.fill(BLACK) # Clear the screen

        if game_state == GameState.MENU:
            text = font.render("Press 1 for Single Player", True, WHITE)
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
            screen.blit(text, text_rect)
            text = font.render("Press 2 for Multiplayer", True, WHITE)
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(text, text_rect)
            text = font.render("Press L to Load Game", True, WHITE)
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
            screen.blit(text, text_rect)

        elif game_state == GameState.PLAYING:
            player_group.draw(screen)
            enemies.draw(screen)
            blocks.draw(screen)
            powerups.draw(screen)

            # Display score and health
            score_text = font.render(f"Score: {score}", True, WHITE)
            screen.blit(score_text, (10, 10))
            health_text = font.render(f"Health: {player_health}", True, WHITE)
            screen.blit(health_text, (10, 40))
            level_text = font.render(f"Level: {level}", True, WHITE)
            screen.blit(level_text, (10, 70))
        elif game_state == GameState.PAUSED:
            text = font.render("Game Paused - Press P to resume, S to save and return to Menu", True, WHITE)
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(text, text_rect)
        elif game_state == GameState.GAME_OVER:
            text = font.render("Game Over! Press R to Restart, M for Menu", True, WHITE)
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(text, text_rect)
            score_text = font.render(f"Final Score: {score}", True, WHITE)
            score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
            screen.blit(score_text, score_rect)
        elif game_state == 4: #Multiplayer Menu
            text = font.render("Press 1 to Host Multiplayer", True, WHITE)
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
            screen.blit(text, text_rect)
            text = font.render("Press 2 to Join Multiplayer", True, WHITE)
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(text, text_rect)
            text = font.render("Press Backspace to return to main menu", True, WHITE)
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
            screen.blit(text, text_rect)



        pygame.display.flip() # Update the display

        # Control the FPS
        clock.tick(FPS)

    # Quit Pygame
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()