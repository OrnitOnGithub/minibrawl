# MIT License
# 
# Copyright (c) 2024 Ornithopter747
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
print("Copyright (c) 2024 Ornithopter747")

import threading
import pygame
import socket
import math
import json
import sys

class Vector2:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
    # the below 2 functions dont work idk
    def magnitude(self) -> float:
        return math.sqrt((self.x ** 2.0) + (self.y ** 2.0))
    def normalise(self):
        self.x = self.x / self.magnitude
        self.y = self.y / self.magnitude

class Player:
    def __init__(self, position: Vector2, ip: str, hp=100):
        self.position = position
        self.hp = hp
        self.ip = ip
    
    def to_json(self):
        return  {
            "ip": self.ip,
            "hp": self.hp,
            "position_x": self.position.x,
            "position_y": self.position.y
        }
    def from_json(json):
        return Player(
            position=Vector2(json['position_x'], json['position_y']),
            hp= json["hp"],
            ip= json["ip"]
        )
    
    def __str__(self) -> str:
        return f"pos: x:{self.position.x}, y:{self.position.y}, hp: {self.hp}, ip: {self.ip}"
    
    def draw(self, screen):
        player_size = 30
        rect = pygame.Rect(self.position.x -(player_size/2), self.position.y - (player_size/2), player_size, player_size)
        pygame.draw.rect(screen, (10, 10, 10) , rect)

class Bullet:
    def __init__(self, position: Vector2, rotation: Vector2):
        self.position = position
        self.rotation = rotation

PORT = 25565
players = []
kill_udp_listener = False
def udp_listener(port=PORT):
    global kill_udp_listener
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', port))
    print("UDP listening socket bound.")
    
    while True:

        if kill_udp_listener:
            break

        data, addr = sock.recvfrom(1024)
        data = data.decode('utf-8')
        data = json.loads(data)
        player_data = Player.from_json(data)
        ip = addr[0]
        # print(addr)
        player_data.ip = ip

        for i, existing_player in enumerate(players):
            if existing_player.ip == ip:
                players[i] = player_data
                break
        else:
            players.append(player_data)

        # print(f"Received player update: {player_data}")

print("UDP listening thread started.")
listen_thread = threading.Thread(target=udp_listener)
listen_thread.start()


player = Player(Vector2(10.0, 10.0), ip="0.0.0.0")
speed = 0.300 # Why are you looking at this? are you trying to cheat? bad friend.
movement = Vector2(0.0, 0.0)
mov_right = 0.0
mov_left = 0.0
mov_up = 0.0
mov_down = 0.0
mouse_pos = Vector2(0.0, 0.0)
mouse_pressed = False


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
print("UDP sending socket bound.")

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((1000, 600))
pygame.display.set_caption("Minibrawl")
print("Pygame started.")

running = True
while running:
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False
            kill_udp_listener = True

        # Mouse
        if event.type == pygame.MOUSEMOTION:
            mouse_pos.x = event.pos[0]
            mouse_pos.y = event.pos[1]
        if (event.type == pygame.MOUSEBUTTONDOWN):
            mouse_pressed = True
        if (event.type == pygame.MOUSEBUTTONUP):
            mouse_pressed = False

        
        # Keyboard
        if event.type == pygame.KEYDOWN:
            # Quit the game
            if event.key == pygame.K_ESCAPE:
                running = False
                kill_udp_listener = True
            # Movement input
            if event.key == pygame.K_a:
                mov_left = 1.0
            if event.key == pygame.K_d:
                mov_right = 1.0
            if event.key == pygame.K_w:
                mov_up = 1.0
            if event.key == pygame.K_s:
                mov_down = 1.0
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                mov_left = 0.0
            if event.key == pygame.K_d:
                mov_right = 0.0
            if event.key == pygame.K_w:
                mov_up = 0.0
            if event.key == pygame.K_s:
                mov_down = 0.0
        movement.x = mov_right - mov_left
        movement.y = mov_down - mov_up

        if movement.x ** 2 == 1.0 and movement.y ** 2 == 1.0:
            movement.x /= 1.42
            movement.y /= 1.42
        # print(movement.x, movement.y)

    dt = clock.tick(60)

    player.position.x += movement.x * speed * dt
    player.position.y += movement.y * speed * dt

    if player.position.x > 1000:
        player.position.x = 1000
    if player.position.y > 600:
        player.position.y = 600
    if player.position.y < 0:
        player.position.y = 0
    if player.position.x < 0:
        player.position.x = 0

    # print("SELF:", player)
    # print(len(players))
    # if len(players) > 0:
    #     print(players[0])

    screen.fill((255, 255, 255))

    pygame.draw.line(start_pos=(player.position.x, player.position.y), end_pos=(mouse_pos.x, mouse_pos.y), width=2, surface=screen, color=(255, 0, 0))

    # player.draw(screen)

    for other_player in players:
        other_player.draw(screen)

    try:
        json_player = player.to_json()
        packet_json = json.dumps(json_player)
        sock.sendto(packet_json.encode(), ('<broadcast>', PORT))
        # print(f"Sent player update: {json_player}")
    except Exception as e:
        print(f"Error sending player update: {e}")


    pygame.display.flip()
pygame.quit()
sys.exit()