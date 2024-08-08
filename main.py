import pygame as pg
from game import Game

pg.init()

# Constants
DIMENSIONS = (1200, 800)
CLOCk = pg.time.Clock()
FPS = 60

window = pg.display.set_mode(DIMENSIONS)
pg.display.set_caption('Tic Tac Toe')
play = True

# Components
game = Game(window)
restart = False

while(play):
    
    window.fill((255, 255, 255))

    for event in pg.event.get():
        if event.type == pg.QUIT:
            play = False
            break
        restart = game.handleEvents(event)
    
    if restart:
        game = Game(window)
    
    game.play()
    pg.display.update()
    CLOCk.tick(FPS)