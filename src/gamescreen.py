from os import path
import pygame

from settings import GameState
from player import Player
from maps import Map


class GameScreen(object):

    def __init__(self, screen, game_settings):

        self.screen = screen
        self.screen_rect = self.screen.get_rect()
        self.game_settings = game_settings
        self.input = game_settings.input

        # Map
        level_path = path.dirname(path.realpath("resources"))
        self.map = Map(self.screen, self.game_settings, path.join(level_path, 'level_01.txt'))
        self.cur_zone = self.map.zones[self.map.spawnpoint[0]][self.map.spawnpoint[1]]

        spawn = self.map.zones[self.map.spawnpoint[0]][self.map.spawnpoint[1]]
        self.player = Player(self.screen, game_settings, spawn.leftspawn[0], spawn.leftspawn[1])

    def screen_start(self):
        pygame.mixer.music.stop()

        # Sets player keys and spawn
        self.input = self.game_settings.input

        #sets player ground
        self.player.ground = self.cur_zone.leftspawn[1]

    def check_collisions(self, collidable):
        while self.cur_zone.collision_by_x(self.player, collidable):
            if collidable.moving and self.player.vel_x == 0:
                #if the player is colliding with a moving object
                #and the player isnt moving, then move the player the same direction
                #the object they are colliding with is moving
                vel = 1
                if not collidable.facing_right:
                    vel = -1
            else:
                #otherwise, move them normally to fix collision
                #if x is causing collision, move x back by 1
                vel = 1
                if self.player.facing_right:
                    #if moving left, vel is negative
                    vel = -1

            self.player.move_by_amount(vel, 0)
        
        yfixed = False
        while self.cur_zone.collision_by_y(self.player, collidable):
            yfixed = True
            if collidable.moving and (self.player.vel_y == 0 or self.player.vel_y == -1):
            #if the player is colliding with a moving object
            #and the player isnt moving, then move the player the same direction
            #the object they are colliding with is moving
                vel = 1
                if collidable.vel_y <= 0:
                    vel = -1
            else:
                vel = 1
                if self.player.vel_y < 0:
                    vel = -1

            #if y is causing collision, move y back by 1
            self.player.move_by_amount(0, vel)

        moving_collidable = None
        if yfixed and collidable.moving:
        #if the player is colliding with a moving object
        #then return the collidable to do things with later
            moving_collidable = collidable
        return (yfixed, moving_collidable)

    def update(self):
        self.player.move()
        self.cur_zone.update_enemies(self.player)

        yfixed = False
        moving_collidable = None
        for collidable in self.cur_zone.collidables:
            ret_vals = self.check_collisions(collidable)
            if ret_vals[0]:
                yfixed = True
            if ret_vals[1] is not None:
                moving_collidable = ret_vals[1]

        for collidable in self.cur_zone.enemies:
            ret_vals = self.check_collisions(collidable)
            if ret_vals[0]:
                yfixed = True
            if ret_vals[1] is not None:
                moving_collidable = ret_vals[1]

        print(yfixed)
        #reset player jump
        if(yfixed):
            self.player.jumping = False
            self.player.vel_y = 0
            
        if moving_collidable is not None and moving_collidable.vel_y > 0 and self.player.y < moving_collidable.y:
        #if we are moving down on top of a collidable
        #then snap the player to the top of the collidable
        #and match vel_y
        #also add collidables vel_x, so collidable carries player
            self.player.get_rect().bottom = moving_collidable.get_rect().top
            self.player.vel_y = -moving_collidable.vel_y
            self.player.x += moving_collidable.vel_x

        if moving_collidable is not None and moving_collidable.vel_y <= 0 and self.player.y < moving_collidable.y:
        #if we are moving up on top of a collidable
        #the add collidables vel_x, so collidable carries player
            self.player.x += moving_collidable.vel_x

        self.cur_zone.check_oob(self.player)


    def check_events(self):

        ret_game_state = GameState(3)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                ret_game_state = GameState.QUIT

            elif event.type == pygame.KEYDOWN:

                if event.key == self.input['up']:
                    self.player.jump()
                    pass

                if event.key == self.input['left']:
                    self.player.move_left()

                if event.key == self.input['right']:
                    self.player.move_right()

            elif event.type == pygame.KEYUP:

                if event.key == self.input['left']:
                    self.player.move_left(False)

                if event.key == self.input['right']:
                    self.player.move_right(False)

        return ret_game_state

    def screen_end(self):
        pass

    def blitme(self):

        self.cur_zone.blitme()
        #pygame.draw.rect(self.screen,(111,111,111),self.player.get_rect())
        self.player.blitme()
