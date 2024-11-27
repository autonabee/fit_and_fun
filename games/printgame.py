#!/usr/bin/python3
import pygame as pg

pg.init()
screen = pg.display.set_mode((1280, 720))
myfont = pg.font.SysFont("monospace", 35)
clock = pg.time.Clock()


turning = False
run = True
while run:
    screen.fill("purple")
    for e in pg.event.get():
        if e.type == pg.QUIT:
            run = False
    turning = pg.key.get_pressed()[pg.K_a]
            
    s = "turning" if turning else "still"
    label = myfont.render(f"the wheel of fortune is {s}...", 1, (255,255,0))
    screen.blit(label, (100, 100))
    pg.display.flip()

    clock.tick(10)  # limits FPS to 60