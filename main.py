"""
Written by John Jankowski for Python Programming Final Project
"""

import arcade

# width, height = arcade.get_display_size() --- In case I want to change based on computer screen size
SCALE = .5
PLAYER_SCALE = .7
TILE_SIZE = 80*SCALE
SCREEN_WIDTH = 1040*SCALE
SCREEN_HEIGHT = 1040*SCALE
SCREEN_TITLE = "Frogger"


class StartView(arcade.View):

    def on_show(self):
        arcade.set_background_color(arcade.csscolor.DARK_SLATE_BLUE)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text("Move the frog to the lily pads,\navoiding water and cars", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                         arcade.color.WHITE, font_size=30, anchor_x="center")
        arcade.draw_text("Click to advance", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 75,
                         arcade.color.WHITE, font_size=20, anchor_x="center")

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        """ If the user presses the mouse button, start the game. """
        game_view = GameView()
        game_view.setup()
        self.window.show_view(game_view)


class GameOverView(arcade.View):

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text("You Won!", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                         arcade.color.WHITE, font_size=40, anchor_x="center")
        arcade.draw_text("Click to play again", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 75,
                         arcade.color.WHITE, font_size=20, anchor_x="center")

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        """ If the user presses the mouse button, re-start the game. """
        game_view = GameView()
        game_view.setup()
        self.window.show_view(game_view)


class Player(arcade.Sprite):

    def __init__(self, filename, scale):
        super().__init__(filename, scale)
        self.on_safe = False

    def update(self):
        super().update()
        # Check for out-of-bounds
        if self.left < 0:
            self.center_x, self.center_y = SCREEN_WIDTH/2, TILE_SIZE/2
        elif self.right > SCREEN_WIDTH - 1:
            self.center_x, self.center_y = SCREEN_WIDTH/2, TILE_SIZE/2

        if self.bottom < 0:
            self.bottom = 0
        elif self.top > SCREEN_HEIGHT - 1:
            self.top = SCREEN_HEIGHT - 1


class Obstacle(arcade.Sprite):

    def __init__(self, filename, scale, safe):
        super().__init__(filename, scale)
        # Whether obstacle will cause you to lose or not
        self.safe = safe


class Log(Obstacle):
    def __init__(self, filename, scale, safe, size):
        super().__init__(filename, scale, safe)
        if size == 'small':
            self.velocity = (-2, 0)
        if size == 'med':
            self.velocity = (-1.5, 0)
        if size == 'big':
            self.velocity = (-1, 0)

    def update(self):
        super().update()

        if self.right < 0:
            self.left = SCREEN_WIDTH


class Turtle(Obstacle):
    def __init__(self, filename, scale, safe, place):
        super().__init__(filename, scale, safe)
        self.velocity = (1.75, 0)
        self.place = place

    def update(self):
        super().update()

        if self.left > SCREEN_WIDTH:
            self.right = -TILE_SIZE


class YellowCar(Obstacle):
    def __init__(self, filename, scale, safe):
        super().__init__(filename, scale, safe)
        self.velocity = (-3, 0)

    def update(self):
        super().update()

        if self.right < 0:
            self.left = SCREEN_WIDTH


class GreenCar(Obstacle):
    def __init__(self, filename, scale, safe):
        super().__init__(filename, scale, safe)
        self.velocity = (1.5, 0)

    def update(self):
        super().update()

        if self.left > SCREEN_WIDTH:
            self.right = -2*TILE_SIZE


class BlueCar(Obstacle):
    def __init__(self, filename, scale, safe):
        super().__init__(filename, scale, safe)
        self.velocity = (2, 0)

    def update(self):
        super().update()

        if self.left > SCREEN_WIDTH:
            self.right = 0


class BigRig(Obstacle):
    def __init__(self, filename, scale, safe):
        super().__init__(filename, scale, safe)
        self.velocity = (.5, 0)

    def update(self):
        super().update()

        if self.left > SCREEN_WIDTH:
            self.right = -2*TILE_SIZE


class FireTruck(Obstacle):
    def __init__(self, filename, scale, safe):
        super().__init__(filename, scale, safe)
        self.velocity = (-1, 0)

    def update(self):
        super().update()

        if self.right < 0:
            self.left = SCREEN_WIDTH


class GameView(arcade.View):

    def __init__(self):
        super().__init__()

        self.ground_list = None
        self.water_list = None
        self.lily_pad_list = None
        self.end_ground_list = None
        self.occupied_pad_list = None

        self.player = None
        self.all_obstacles = None

        self.setup()

    def setup(self):
        my_map = arcade.read_tmx("map.tmx")

        self.all_obstacles = arcade.SpriteList()
        # Terrain
        self.ground_list = arcade.process_layer(my_map, "ground", SCALE,  use_spatial_hash=True)
        self.water_list = arcade.process_layer(my_map, "water", SCALE, use_spatial_hash=True)
        self.lily_pad_list = arcade.process_layer(my_map, "lilypads", SCALE, use_spatial_hash=True)
        self.end_ground_list = arcade.process_layer(my_map, "end", SCALE, use_spatial_hash=True)
        self.occupied_pad_list = arcade.SpriteList()

        # Safe Obstacles
        self.init_turtles()
        self.init_logs()

        # Dangerous Obstacles
        self.init_yellow_cars()
        self.init_green_cars()
        self.init_blue_cars()
        self.init_big_rigs()
        self.init_firetrucks()

        # Player
        self.player = Player("images/frog.png", PLAYER_SCALE)
        self.player.center_x = SCREEN_WIDTH/2
        self.player.center_y = TILE_SIZE/2

    def init_turtles(self):
        for i in ((.5, 'left'), (1.5, 'middle'), (2.5, 'right'), (5.5, 'left'), (6.5, 'middle'), (7.5, 'right'),
                  (10.5, 'left'), (11.5, 'middle'), (12.5, 'right')):
            t = Turtle("images/turtle.png", SCALE, True, i[1])
            t.center_x, t.center_y = i[0]*TILE_SIZE, 7.5*TILE_SIZE
            self.all_obstacles.append(t)
        for i in ((2.5, 'left'), (3.5, 'middle'), (4.5, 'right'), (7.5, 'left'), (8.5, 'middle'), (9.5, 'right')):
            t = Turtle("images/turtle.png", SCALE, True, i[1])
            t.center_x, t.center_y = i[0] * TILE_SIZE, 10.5 * TILE_SIZE
            self.all_obstacles.append(t)

    def init_logs(self):
        for i in (2, 6, 10):
            log1 = Log("images/small_log.png", SCALE, True, 'small')
            log1.center_x, log1.center_y = i*TILE_SIZE, 8.5*TILE_SIZE
            self.all_obstacles.append(log1)
        for i in (3, 10):
            log1 = Log("images/big_log.png", SCALE, True, 'big')
            log1.center_x, log1.center_y = i * TILE_SIZE, 9.5 * TILE_SIZE
            self.all_obstacles.append(log1)
        for i in (4, 11):
            log1 = Log("images/med_log.png", SCALE, True, 'med')
            log1.center_x, log1.center_y = i * TILE_SIZE, 11.5 * TILE_SIZE
            self.all_obstacles.append(log1)

    def init_yellow_cars(self):
        for i in (4, 9):
            car1 = YellowCar("images/yellow_car.png", SCALE, False)
            car1.center_x, car1.center_y = i*TILE_SIZE, 5.5*TILE_SIZE
            self.all_obstacles.append(car1)

    def init_green_cars(self):
        for i in (1, 4, 9, 12):
            car1 = GreenCar("images/green_car.png", SCALE, False)
            car1.center_x, car1.center_y = i * TILE_SIZE, 4.5 * TILE_SIZE
            self.all_obstacles.append(car1)

    def init_blue_cars(self):
        for i in (2, 7, 12):
            car1 = BlueCar("images/blue_car.png", SCALE, False)
            car1.center_x, car1.center_y = i*TILE_SIZE, 1.5 * TILE_SIZE
            self.all_obstacles.append(car1)

    def init_big_rigs(self):
        for i in (2, 10):
            rig1 = BigRig("images/big_rig.png", SCALE, False)
            rig1.center_x, rig1.center_y = i*TILE_SIZE, 3.5*TILE_SIZE
            self.all_obstacles.append(rig1)

    def init_firetrucks(self):
        for i in (4, 11):
            truck1 = FireTruck("images/firetruck.png", SCALE, False)
            truck1.center_x, truck1.center_y = i*TILE_SIZE, 2.5*TILE_SIZE
            self.all_obstacles.append(truck1)

    def on_draw(self):
        arcade.start_render()
        self.ground_list.draw()
        self.water_list.draw()
        self.all_obstacles.draw()
        self.end_ground_list.draw()
        self.lily_pad_list.draw()
        self.occupied_pad_list.draw()
        self.player.draw()

    def on_key_press(self, key, modifiers):
        self.player.on_safe = False
        self.player.velocity = (0, 0)
        if key == arcade.key.UP:
            self.player.center_y += TILE_SIZE
        elif key == arcade.key.DOWN:
            self.player.center_y += -TILE_SIZE
        elif key == arcade.key.LEFT:
            self.player.center_x += -TILE_SIZE
        elif key == arcade.key.RIGHT:
            self.player.center_x += TILE_SIZE

    def on_update(self, delta_time):
        self.player.update()
        self.all_obstacles.update()

        hit_list = arcade.check_for_collision_with_list(self.player, self.all_obstacles)
        for o in hit_list:
            # safe obstacles
            if o.safe and (type(o) is Log) and (self.player.left >= o.left - 15) and (self.player.right <= o.right + 15):
                self.player.velocity = o.velocity
                self.player.on_safe = True
            if o.safe and (type(o) is Turtle):
                if (o.place == 'left') and (self.player.left >= o.left - 15):
                    self.player.velocity = o.velocity
                    self.player.on_safe = True
                elif o.place == 'middle':
                    self.player.velocity = o.velocity
                    self.player.on_safe = True
                elif (o.place == 'right') and (self.player.right <= o.right + 15):
                    self.player.velocity = o.velocity
                    self.player.on_safe = True
            # run into dangerous obstacle
            if not o.safe:
                self.player.center_x, self.player.center_y = SCREEN_WIDTH/2, TILE_SIZE/2

        water_hit_list = arcade.check_for_collision_with_list(self.player, self.water_list)
        for w in water_hit_list:
            if not self.player.on_safe:
                self.player.center_x, self.player.center_y = SCREEN_WIDTH / 2, TILE_SIZE / 2

        lily_pad_hit_list = arcade.check_for_collision_with_list(self.player, self.lily_pad_list)
        for p in lily_pad_hit_list:
            if p not in self.occupied_pad_list:
                end_frog = arcade.Sprite("images/frog_end.png", PLAYER_SCALE)
                end_frog.center_x, end_frog.center_y = p.center_x, p.center_y
                self.occupied_pad_list.append(end_frog)
                self.player.center_x, self.player.center_y = SCREEN_WIDTH / 2, TILE_SIZE / 2

        end_hit_list = arcade.check_for_collision_with_list(self.player, self.end_ground_list)
        for e in end_hit_list:
            self.player.center_x, self.player.center_y = SCREEN_WIDTH / 2, TILE_SIZE / 2

        if len(self.occupied_pad_list) == 5:
            view = GameOverView()
            self.window.show_view(view)


if __name__ == '__main__':
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    start_view = StartView()
    window.show_view(start_view)
    arcade.run()


