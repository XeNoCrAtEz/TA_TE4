import pygame
import numpy as np
from utils import *

class Point:
    def __init__(self, point: list, isScreenCoord: bool = True) -> None:
        if isScreenCoord:
            self.screenX, self.screenY = point
            self.cartX, self.cartY = to_cart_coord(point)
        else:
            self.screenX, self.screenY = to_screen_coord(point)
            self.cartX, self.cartY = point
        
    def get_screen_point(self) -> list:
        return [self.screenX, self.screenY]

    def get_cart_point(self) -> list:
        return [self.cartX, self.cartY]

    def __str__(self) -> str:
        return "screen coord: ({}, {})\ncartesian coord: ({}, {})".format(self.screenX, self.screenY, self.cartX, self.cartY)

    
class SamplePoint():
    def __init__(
            self, pos: Point, samplePointNum: int,
            color: tuple
    ) -> None:
        self.samplePointNum = samplePointNum
        self.radius: int = 10
        self.range: int = 300
        self.deltaTheta: int = 36
        self.pos: Point = pos
        self.color: tuple = color
        self.AoA: float = None
        self.AoAEndPos: Point = None

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        pygame.draw.circle(surface, self.color, self.pos.get_screen_point(), self.radius)

        if not self.AoAEndPos: raise ValueError("AoA not calculated yet!")       # don't continue if AoA not determined yet

        surface.blit(
            font.render('L'+str(self.samplePointNum), False, (255,255,255)),
            self.pos.get_screen_point()
        )
        if self.AoA:
            surface.blit(
                font.render('{:.2f}'.format(self.AoA), False, (255,255,255)), 
                (self.pos.screenX, self.pos.screenY+20)
            )
        surface.blit(
            font.render(str(self.pos.get_screen_point()), False, (255,255,255)),
            (self.pos.screenX, self.pos.screenY+40)
        )
    

        # draw sensing delta theta
        for i in range(0, int(self.deltaTheta/2+1),3):
            pygame.draw.line(surface, (255,255,255), self.pos.get_screen_point(), 
                (self.pos.screenX + self.range*np.cos((self.AoA-i)*np.pi/180),
                 self.pos.screenY - self.range*np.sin((self.AoA-i)*np.pi/180)), 2
            )
            pygame.draw.line(surface, (255,255,255), self.pos.get_screen_point(),
                (self.pos.screenX + self.range*np.cos((self.AoA+i)*np.pi/180),
                 self.pos.screenY - self.range*np.sin((self.AoA+i)*np.pi/180)), 2
            )

        # draw sensing max range
        pygame.draw.arc(
            surface,
            (255,255,255), 
            (self.pos.screenX-self.range, self.pos.screenY-self.range, self.range*2, self.range*2), 
            (self.AoA-self.deltaTheta/2)*np.pi/180,
            (self.AoA+self.deltaTheta/2)*np.pi/180, 
            2
        )

        # draw AoA line
        pygame.draw.line(surface, (80,80,80), self.pos.get_screen_point(), self.AoAEndPos.get_screen_point(), 3)

    def calcAoA(self, AoAEndPos: Point) -> None:
        self.AoAEndPos = AoAEndPos
        dy = AoAEndPos.cartY-self.pos.cartY
        dx = AoAEndPos.cartX-self.pos.cartX
        self.AoA = to_deg(np.arctan2(dy, dx))
        if self.AoA < 0: self.AoA += 360
        print(self.AoA)