import arcade
import math

# A tower sits on the ground and waits for enemies.
# It can shoot the bad guys when they get close.
class Tower(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__("place.png")
        self.center_x = x
        self.center_y = y
        self.scale = 1
        self.time_since_last_shot = 0.0

# An enemy walks along the path.
# It has health and can move from one point to the next.
class Enemy(arcade.Sprite):
    def __init__(self, path_points):
        super().__init__("enemy.png")
        self.path_points = path_points
        self.current_target = 1
        self.health = 5
        self.speed = 180
        self.center_x, self.center_y = path_points[0]

    # Move the enemy a little bit every time the game updates.
    def update(self, delta_time):
        if self.current_target >= len(self.path_points):
            return
        target_x, target_y = self.path_points[self.current_target]
        dx = target_x - self.center_x
        dy = target_y - self.center_y
        distance = math.hypot(dx, dy)
        if distance == 0:
            self.current_target += 1
            return
        move_distance = self.speed * delta_time
        if move_distance >= distance:
            self.center_x = target_x
            self.center_y = target_y
            self.current_target += 1
        else:
            self.center_x += dx / distance * move_distance
            self.center_y += dy / distance * move_distance

# A bullet is a little flying thing that comes from the tower.
class Bullet(arcade.Sprite):
    def __init__(self, x, y, dx, dy):
        super().__init__("bullet.png")
        self.center_x = x
        self.center_y = y
        self.scale = 1
        self.velocity_x = dx
        self.velocity_y = dy

    # Move the bullet in a straight line every frame.
    def update(self, delta_time):
        self.center_x += self.velocity_x * 2 * delta_time
        self.center_y += self.velocity_y * 2 * delta_time

# This is the main game window where everything happens.
class TowerDefense(arcade.Window):

    def __init__(self):
        super().__init__(1500, 800, ("accurate defense simulator"))

        arcade.set_background_color(arcade.color.DIRT)

        self.paths = arcade.SpriteList()
        self.towers = arcade.SpriteList()
        self.enemies = arcade.SpriteList()
        self.bullets = arcade.SpriteList()
        self.buttons = arcade.SpriteList()
        self.placing_mode = False
        self.path_positions = []
        self.spawn_timer = 0.0

        # This is the picture that shows where a tower can go.
        self.preview = arcade.Sprite("place.png")
        self.preview.scale = 1
        self.preview.alpha = 120
        self.preview.color = arcade.color.WHITE
        self.preview.position = (0, 0)

        self.button_texture = arcade.load_texture("mutton.png")
        self.button_exit_texture = arcade.load_texture("exit.png")
        self.button = arcade.Sprite("mutton.png")
        self.button.scale = 1
        self.button.position = (50, 50)
        self.buttons.append(self.button)

        self.pathx = 50
        self.pathy = 650
        self.money = 500
        self.reset_game()

    def reset_game(self):
        self.paths = arcade.SpriteList()
        self.towers = arcade.SpriteList()
        self.enemies = arcade.SpriteList()
        self.bullets = arcade.SpriteList()
        self.placing_mode = False
        self.spawn_timer = 0.0
        self.path_positions = []
        self.money = 500
        self.preview.position = (0, 0)
        self.pathx = 50
        self.pathy = 650

        # This makes one piece of the path for enemies to walk on.
        def add_path_tile(texture, angle, advance_x, advance_y):
            path = arcade.Sprite(texture)
            path.scale = 2
            path.position = (self.pathx, self.pathy)
            path.angle = angle
            self.paths.append(path)
            self.path_positions.append((self.pathx, self.pathy))
            self.pathx += advance_x
            self.pathy += advance_y

        # Make a straight line of path pieces.
        def Path(repeat, angle2set):
            for _ in range(repeat):
                if angle2set == 0:
                    add_path_tile("gerade.png", 0, 100, 0)
                elif angle2set == 90:
                    add_path_tile("gerade.png", 90, 0, 100)
                elif angle2set == 180:
                    add_path_tile("gerade.png", 180, -100, 0)
                elif angle2set == 270:
                    add_path_tile("gerade.png", 270, 0, -100)

        # Make a curve piece so the path can turn.
        def Curve(angle, adjustposition):
            advance_x = 0
            advance_y = 0
            if adjustposition == 1:
                advance_x = 100
            elif adjustposition == 2:
                advance_y = 100
            elif adjustposition == 3:
                advance_x = -100
            elif adjustposition == 4:
                advance_y = -100
            add_path_tile("curve.png", angle, advance_x, advance_y)

        Path(4, 0)
        Curve(270, 4)
        Path(2, 270)
        Curve(90, 1)
        Path(4, 0)
        Curve(0, 2)
        Path(3, 90)
        Curve(180, 1)
        Path(1, 0)
        Curve(270, 4)
        Path(6, 270)
        Curve(90, 1)
        Path(1, 0)
        Curve(0, 2)
        Curve(180, 1)
        Path(1, 0)


    # Draw all the game pieces on the screen.
    def on_draw(self):
        self.clear()
        self.paths.draw()
        self.enemies.draw()
        self.bullets.draw()
        self.towers.draw()
        self.buttons.draw()

        if self.placing_mode:
            self.button.texture = self.button_exit_texture
            self.button.position = (50, 50)
            if arcade.check_for_collision_with_list(self.preview, self.paths) or self.money < 250:
                self.preview.color = arcade.color.RED
            elif arcade.check_for_collision_with_list(self.preview, self.towers):
                self.preview.color = arcade.color.RED
            else:
                self.preview.color = arcade.color.WHITE
            arcade.draw_sprite(self.preview)
        else:
            self.button.texture = self.button_texture
            self.button.position = (50, 50)

        arcade.draw_text(
            f"Money: ${self.money}",
            10,
            self.height - 30,
            arcade.color.LAWN_GREEN,
            20,
            anchor_x="left",
            anchor_y="bottom",
        )

    # Move the preview helper with the mouse if we are placing a tower.
    def on_mouse_motion(self, x, y, dx, dy):
        if self.placing_mode:
            self.preview.position = (x, y)

    # When the mouse is clicked, either start/stop placing a tower or place one.
    def on_mouse_press(self, x, y, button, modifiers):
        COIN_SOUND = arcade.load_sound("ksjsbwuil-cash-register-1-513922.mp3")
        if button == arcade.MOUSE_BUTTON_LEFT and self.button.collides_with_point((x, y)):
            self.placing_mode = not self.placing_mode
            if self.placing_mode:
                self.preview.position = (x, y)
            return

        if not self.placing_mode:
            return

        if button == arcade.MOUSE_BUTTON_LEFT:
            if self.money >= 250:
                tower = Tower(x, y)
                if arcade.check_for_collision_with_list(tower, self.paths):
                    print("You can't place a tower on the path!")
                elif arcade.check_for_collision_with_list(tower, self.towers):
                    print("You can't place a tower on top of another tower!")
                else:
                    self.towers.append(tower)
                    self.money -= 250
                    self.coin_playback = COIN_SOUND.play()
                    self.placing_mode = not self.placing_mode
            else:
                print("Not enough money to place a tower!")

    # Find the closest enemy to a tower so it can shoot the right one.
    def get_nearest_enemy(self, sprite):
        if len(self.enemies) == 0:
            return None
        return min(self.enemies, key=lambda enemy: arcade.get_distance_between_sprites(sprite, enemy))

    # Create a new enemy and send it onto the path.
    def spawn_enemy(self):
        if not self.path_positions:
            return
        enemy = Enemy(self.path_positions)
        self.enemies.append(enemy)

    # Update the whole game. This runs many times every second.
    def on_update(self, delta_time):
        self.spawn_timer += delta_time
        if self.spawn_timer >= 10.0:
            self.spawn_timer -= 10.0
            self.spawn_enemy()

        # Move each enemy and remove it when it reaches the end.
        for enemy in list(self.enemies):
            enemy.update(delta_time)
            if enemy.current_target >= len(enemy.path_points):
                self.enemies.remove(enemy)
                self.reset_game()
                return

        # Move bullets and remove ones that fly off the screen.
        for bullet in list(self.bullets):
            bullet.update(delta_time)
            if (
                bullet.center_x < 0
                or bullet.center_x > self.width
                or bullet.center_y < 0
                or bullet.center_y > self.height
            ):
                self.bullets.remove(bullet)

        # Make each tower look for an enemy and shoot if it can.
        for tower in self.towers:
            target = self.get_nearest_enemy(tower)
            if target:
                dx = target.center_x - tower.center_x
                dy = target.center_y - tower.center_y
                angle = 270 - math.degrees(math.atan2(dy, dx))
                tower.angle = angle % 360
                tower.time_since_last_shot += delta_time
                if tower.time_since_last_shot >= 0.5:
                    tower.time_since_last_shot -= 0.5
                    distance = math.hypot(dx, dy)
                    if distance > 0:
                        direction_x = dx / distance
                        direction_y = dy / distance
                        bullet_speed = 400
                        bullet = Bullet(
                            tower.center_x,
                            tower.center_y,
                            direction_x * bullet_speed,
                            direction_y * bullet_speed,
                        )
                        self.bullets.append(bullet)

        # If a bullet hits an enemy, make the enemy lose health.
        for bullet in list(self.bullets):
            enemies_hit = arcade.check_for_collision_with_list(bullet, self.enemies)
            for enemy in enemies_hit:
                if bullet in self.bullets:
                    self.bullets.remove(bullet)
                enemy.health -= 1
                if enemy.health <= 0 and enemy in self.enemies:
                    self.enemies.remove(enemy)
                    self.money += 100
                break

TowerDefense()

arcade.run()