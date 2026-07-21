import arcade #link of the arcade documentation: https://api.arcade.academy/en/latest/index.html
import math
import os
import platform
import warnings

warnings.filterwarnings("ignore")

# This is a tower defense game.
# Players place towers to stop enemies before they reach the end of the path.

# A tower sits on the ground and waits for enemies.
# It can shoot the bad guys when they get close.
class Tower(arcade.Sprite):
    def __init__(self, x, y, tower_type="basic"):
        self.tower_type = tower_type
        # Different tower types cost different money and shoot in different ways.
        if tower_type == "cannon":
            initial_texture = "cannon-1.png"
            self.texture_files = ["cannon-1.png", "cannon-2.png", "cannon-3.png", "cannon-4.png"]
            self.upgrade_costs = [600, 1000, 1500]
            self.purchase_cost = 400
            self.range = 220
            self.shoot_interval = 1.5
            self.damage = 5
        else:
            initial_texture = "place.png"
            self.texture_files = ["place.png", "place-1.png", "place-2.png", "place-3.png"]
            self.upgrade_costs = [250, 500, 1000]
            self.purchase_cost = 250
            self.range = 200
            self.shoot_interval = 0.5
            self.damage = 1

        super().__init__(initial_texture)
        self.center_x = x
        self.center_y = y
        if tower_type == "cannon":
            self.scale = 1.25
        else:
            self.scale = 1
        self.time_since_last_shot = 0.0
        self.upgrade_level = 0
        self.total_spent = self.purchase_cost
        self.texture = arcade.load_texture(self.texture_files[0])

    def get_upgrade_cost(self):
        if self.upgrade_level >= len(self.upgrade_costs):
            return None
        return self.upgrade_costs[self.upgrade_level]

    def can_upgrade(self):
        return self.get_upgrade_cost() is not None

    def get_sell_value(self):
        return int(self.total_spent * 0.5)

    def apply_upgrade(self):
        if not self.can_upgrade():
            return False
        cost = self.get_upgrade_cost()
        self.upgrade_level += 1
        self.texture = arcade.load_texture(self.texture_files[min(self.upgrade_level, len(self.texture_files) - 1)])
        if self.tower_type == "cannon":
            self.range += 30
            self.damage += 2
            self.shoot_interval -= 0.125
        else:
            self.range = 200 + self.upgrade_level * 60
            self.shoot_interval = max(0.2, 0.5 - (self.upgrade_level - 1) * 0.1)
            self.damage += 1
        self.total_spent += cost
        return True

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
        self.distance_to_goal = self.get_distance_to_goal()

    def get_distance_to_goal(self):
        if self.current_target >= len(self.path_points):
            return 0

        remaining_distance = math.hypot(
            self.path_points[self.current_target][0] - self.center_x,
            self.path_points[self.current_target][1] - self.center_y,
        )

        for index in range(self.current_target, len(self.path_points) - 1):
            start_x, start_y = self.path_points[index]
            end_x, end_y = self.path_points[index + 1]
            remaining_distance += math.hypot(end_x - start_x, end_y - start_y)

        return remaining_distance

    # Move the enemy a little bit every time the game updates.
    def update(self, delta_time):
        if self.current_target >= len(self.path_points):
            self.distance_to_goal = 0
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

        self.distance_to_goal = self.get_distance_to_goal()

# Some enemies are special.
# Speedy ones are fast, tanks are tough, and cool enemies have a middle balance.
class SpeedyEnemy(Enemy):
    def __init__(self, path_points):
        super().__init__(path_points)
        self.texture = arcade.load_texture("speedy.png")
        self.health = 3
        self.speed = 270
        self.distance_to_goal = 3100


class TankEnemy(Enemy):
    def __init__(self, path_points):
        super().__init__(path_points)
        self.texture = arcade.load_texture("tank.png")
        self.health = 15
        self.speed = 120
        self.distance_to_goal = 3100

class CoolEnemy(Enemy):
    def __init__(self, path_points):
        super().__init__(path_points)
        self.texture = arcade.load_texture("idkwhattonamethis.png")
        self.health = 7
        self.speed = 200
        self.distance_to_goal = 3100

# A bullet is a little flying thing that comes from the tower.
class Bullet(arcade.Sprite):
    def __init__(self, x, y, dx, dy, damage, scale=1):
        super().__init__("bullet.png")
        self.center_x = x
        self.center_y = y
        self.scale = scale
        self.velocity_x = dx
        self.velocity_y = dy
        self.damage = damage

    # Move the bullet in a straight line every frame.
    def update(self, delta_time):
        self.center_x += self.velocity_x * 2 * delta_time
        self.center_y += self.velocity_y * 2 * delta_time

# This is the main game window where everything happens.
class TowerDefense(arcade.Window):

    def __init__(self):
        super().__init__(1500, 800, ("Circle vs Square TD"))

        arcade.set_background_color(arcade.color.DIRT)

        self.paths = arcade.SpriteList()
        self.towers = arcade.SpriteList()
        self.enemies = arcade.SpriteList()
        self.bullets = arcade.SpriteList()
        self.buttons = arcade.SpriteList()
        self.placing_mode = False
        self.path_positions = []
        self.spawn_timer = 0.0
        self.round_number = 1
        self.spawned_this_round = 0
        self.enemies_to_spawn = 0
        self.round_spawn_interval = 1.5
        self.transparent_color = (0, 0, 0, 50) #arcade forced me to do this manually because it doesn't support alpha in arcade.draw_circle_filled() for some reason. I don't know why.
        self.hovered_tower = None
        self.money_given_per_enemy = 50
        self.upgrade_mode = False
        self.selected_tower = None
        self.upgrade_menu_open = False
        self.game_state = "menu"
        self.high_score = self.load_high_score()

        # The game can be in a menu, in a round, or showing an upgrade window.
        # These values help the game know what to draw and what to do next.
        self.preview = arcade.Sprite("place.png")
        self.preview.scale = 1
        self.preview.alpha = 120
        self.preview.color = arcade.color.WHITE
        self.preview.position = (0, 0)

        self.button_texture = arcade.load_texture("mutton.png")
        self.button_exit_texture = arcade.load_texture("exit.png")
        self.cannon_button_texture = arcade.load_texture("cannon-button.png")
        self.button = arcade.Sprite("mutton.png")
        self.button.scale = 1
        self.button.position = (50, 50)
        self.cannon_button = arcade.Sprite("cannon-button.png")
        self.cannon_button.scale = 1
        self.cannon_button.position = (150, 50)
        self.buttons.append(self.button)
        self.buttons.append(self.cannon_button)

        self.pathx = 50
        self.pathy = 650
        self.money = 500
        self.reset_game()

    def calculate_round_enemy_count(self):
        return 3 + self.round_number * 2

    def get_high_score_path(self):
        if platform.system() == "Windows":
            base_dir = os.environ.get("APPDATA", os.path.expanduser("~"))
        elif platform.system() == "Darwin":
            base_dir = os.path.expanduser("~/Library/Application Support")
        else:
            base_dir = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))

        os.makedirs(base_dir, exist_ok=True)
        return os.path.join(base_dir, "circle_vs_square_td", "high_score.txt")

    def load_high_score(self):
        score_path = self.get_high_score_path()
        if not os.path.exists(score_path):
            return 0
        try:
            with open(score_path, "r", encoding="utf-8") as handle:
                return max(0, int(handle.read().strip()))
        except (ValueError, OSError):
            return 0

    def save_high_score(self):
        score_path = self.get_high_score_path()
        os.makedirs(os.path.dirname(score_path), exist_ok=True)
        with open(score_path, "w", encoding="utf-8") as handle:
            handle.write(str(self.high_score))

    def update_high_score(self):
        if self.round_number > self.high_score:
            self.high_score = self.round_number
            self.save_high_score()

    def start_round(self):
        self.spawned_this_round = 0
        self.enemies_to_spawn = self.calculate_round_enemy_count()
        self.spawn_timer = 0.0
        self.round_spawn_interval = max(0.1, 1.5 - (self.round_number - 1) * 0.15)
        if self.round_number >= 20:
            self.money_given_per_enemy = max(10, 50 - (self.round_number - 20) * 2)




    def reset_game(self):
        # This starts a fresh game map and resets the player money and round state.
        self.paths = arcade.SpriteList()
        self.towers = arcade.SpriteList()
        self.enemies = arcade.SpriteList()
        self.bullets = arcade.SpriteList()
        self.placing_mode = False
        self.spawn_timer = 0.0
        self.path_positions = []
        self.money = 500
        self.round_number = 1
        self.preview.position = (0, 0)
        self.placing_tower_type = "basic"
        self.pathx = 50
        self.pathy = 650
        self.money_given_per_enemy = 50
        self.upgrade_mode = False
        self.selected_tower = None
        self.upgrade_menu_open = False
        self.hovered_tower = None
        self.start_round()

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
        Path(2, 0)

    def get_upgrade_menu_bounds(self):
        if self.selected_tower and self.selected_tower.center_x > self.width / 2:
            return 20, 320, 320, 620
        return self.width - 320, self.width - 20, 320, 620

    def set_preview_for_tower_type(self, tower_type):
        self.placing_tower_type = tower_type
        if tower_type == "cannon":
            self.preview.texture = arcade.load_texture("cannon-1.png")
        else:
            self.preview.texture = arcade.load_texture("place.png")

    def is_position_valid_for_tower(self, x, y, tower_type=None, sprite=None):
        # This checks whether the chosen spot is safe for a new tower.
        # A tower cannot be placed on the path or too close to other towers.
        if sprite is None:
            sprite = Tower(x, y, tower_type=tower_type or self.placing_tower_type)

        if arcade.check_for_collision_with_list(sprite, self.paths):
            return False
        if arcade.check_for_collision_with_list(sprite, self.towers):
            return False

        clearance = 95 if (tower_type or self.placing_tower_type) == "cannon" else 70
        for path in self.paths:
            if math.hypot(x - path.center_x, y - path.center_y) < clearance:
                return False

        return True

    def get_upgrade_button_rect(self):
        if self.selected_tower and self.selected_tower.center_x > self.width / 2:
            return 20, 230, 260, 80
        return self.width - 280, 230, 260, 80

    def get_sell_button_rect(self):
        if self.selected_tower and self.selected_tower.center_x > self.width / 2:
            return 20, 140, 260, 80
        return self.width - 280, 140, 260, 80

    def get_menu_button_rect(self):
        button_width = 360
        button_height = 100
        left = (self.width - button_width) / 2
        bottom = (self.height - button_height) / 2 - 40
        return left, bottom, button_width, button_height

    def is_click_on_upgrade_button(self, x, y):
        left, bottom, width, height = self.get_upgrade_button_rect()
        return left <= x <= left + width and bottom <= y <= bottom + height

    def is_click_on_sell_button(self, x, y):
        left, bottom, width, height = self.get_sell_button_rect()
        return left <= x <= left + width and bottom <= y <= bottom + height

    # Draw everything that the player should see.
    # The screen changes depending on the menu, the game play, or the upgrade menu.
    def on_draw(self):
        self.clear()

        if self.game_state == "menu":
            arcade.draw_text(
                "Circle vs Square TD",
                self.width / 2,
                self.height * 0.72,
                arcade.color.WHITE,
                64,
                anchor_x="center",
                anchor_y="center",
            )
            arcade.draw_text(
                "Defend the path with towers and survive the rounds!",
                self.width / 2,
                self.height * 0.62,
                arcade.color.LIGHT_GRAY,
                24,
                anchor_x="center",
                anchor_y="center",
            )
            left, bottom, width, height = self.get_menu_button_rect()
            arcade.draw_lrbt_rectangle_filled(left, left + width, bottom, bottom + height, arcade.color.DARK_BLUE)
            arcade.draw_lrbt_rectangle_outline(left, left + width, bottom, bottom + height, arcade.color.WHITE, 3)
            arcade.draw_text(
                "Start Game",
                self.width / 2,
                bottom + height / 2,
                arcade.color.WHITE,
                30,
                anchor_x="center",
                anchor_y="center",
            )
            arcade.draw_text(
                "Click the button or press space to begin.",
                self.width / 2,
                bottom - 40,
                arcade.color.LIGHT_GRAY,
                18,
                anchor_x="center",
                anchor_y="center",
            )
            arcade.draw_text(
                f"High Score: Round {self.high_score}",
                self.width / 8,
                self.height * 0.95,
                arcade.color.GOLD,
                28,
                anchor_x="center",
                anchor_y="center",
            )
            return

        self.paths.draw()
        self.enemies.draw()
        self.bullets.draw()
        self.towers.draw()
        self.buttons.draw()

        if self.hovered_tower:
            if not self.upgrade_menu_open:
                arcade.draw_circle_filled(self.hovered_tower.center_x, self.hovered_tower.center_y, 40, self.transparent_color)

        #totally not copying the ui from bloons tower defense lol
        if self.placing_mode:
            if self.placing_tower_type == "cannon":
                self.preview.scale = 1.25
            else:
                self.preview.scale = 1
            self.button.texture = self.button_exit_texture if self.placing_tower_type == "basic" else self.button_texture
            self.cannon_button.texture = self.button_exit_texture if self.placing_tower_type == "cannon" else self.cannon_button_texture
            self.button.position = (75, 75)
            self.cannon_button.position = (225, 75)
            tower_cost = 400 if self.placing_tower_type == "cannon" else 250
            if self.money < tower_cost:
                self.preview.color = arcade.color.RED
            elif not self.is_position_valid_for_tower(self.preview.center_x, self.preview.center_y, tower_type=self.placing_tower_type):
                self.preview.color = arcade.color.RED
            else:
                self.preview.color = arcade.color.WHITE
            # else: sudo rm -rf /
            arcade.draw_sprite(self.preview)
            arcade.draw_circle_filled(self.preview.center_x, self.preview.center_y, 220 if self.placing_tower_type == "cannon" else 200, self.transparent_color)
        else:
            self.button.texture = self.button_texture
            self.cannon_button.texture = self.cannon_button_texture
            self.button.position = (75, 75)
            self.cannon_button.position = (225, 75)
        arcade.draw_text(
            f"Money: ${self.money}",
            10,
            self.height - 30,
            arcade.color.LAWN_GREEN,
            20,
            anchor_x="left",
            anchor_y="bottom",
        )

        if self.upgrade_menu_open and self.selected_tower:
            left, right, bottom, top = self.get_upgrade_menu_bounds()
            arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, (30, 30, 35, 220))
            arcade.draw_circle_filled(self.selected_tower.center_x, self.selected_tower.center_y, self.selected_tower.range, self.transparent_color)
            arcade.draw_lrbt_rectangle_outline(left, right, bottom, top, arcade.color.WHITE, 2)
            arcade.draw_text(
                "Tower Upgrade",
                (left + right) // 2,
                top - 40,
                arcade.color.WHITE_SMOKE,
                24,
                anchor_x="center",
                anchor_y="bottom",
            )
            arcade.draw_text(
                f"Upgrade Level: {self.selected_tower.upgrade_level + 1}/4",
                left + 20,
                top - 90,
                arcade.color.WHITE_SMOKE,
                20,
                anchor_x="left",
                anchor_y="bottom",
            )
            if self.selected_tower.can_upgrade():
                cost = self.selected_tower.get_upgrade_cost()
                color = arcade.color.LAWN_GREEN if self.money >= cost else arcade.color.RED
                arcade.draw_text(
                    f"Next Upgrade Cost: ${cost}",
                    left + 20,
                    top - 170,
                    color,
                    20,
                    anchor_x="left",
                    anchor_y="bottom",
                    multiline=True,
                    width = right - left - 40
                )
            else:
                arcade.draw_text(
                    "Fully upgraded",
                    left + 20,
                    top - 130,
                    arcade.color.GOLD,
                    20,
                    anchor_x="left",
                    anchor_y="bottom",
                )

            button_left, button_bottom, button_width, button_height = self.get_upgrade_button_rect()
            button_color = arcade.color.GRAY
            label = "Maxed"
            if self.selected_tower.can_upgrade():
                button_color = arcade.color.GREEN if self.money >= self.selected_tower.get_upgrade_cost() else arcade.color.DARK_GREEN
                label = "Upgrade"
            arcade.draw_lrbt_rectangle_filled(button_left, button_left + button_width, button_bottom, button_bottom + button_height, button_color)
            arcade.draw_lrbt_rectangle_outline(button_left, button_left + button_width, button_bottom, button_bottom + button_height, arcade.color.WHITE, 2)
            arcade.draw_text(
                label,
                button_left + button_width // 2,
                button_bottom + 40,
                arcade.color.WHITE_SMOKE,
                20,
                anchor_x="center",
                anchor_y="center",
            )

            sell_left, sell_bottom, sell_width, sell_height = self.get_sell_button_rect()
            arcade.draw_lrbt_rectangle_filled(sell_left, sell_left + sell_width, sell_bottom, sell_bottom + sell_height, arcade.color.RED)
            arcade.draw_lrbt_rectangle_outline(sell_left, sell_left + sell_width, sell_bottom, sell_bottom + sell_height, arcade.color.WHITE, 2)
            arcade.draw_text(
                "Sell",
                sell_left + sell_width // 2,
                sell_bottom + 50,
                arcade.color.WHITE_SMOKE,
                20,
                anchor_x="center",
                anchor_y="center",
            )
            arcade.draw_text(
                f"Sell for: ${self.selected_tower.get_sell_value()}",
                sell_left + sell_width // 2,
                sell_bottom + 7,
                arcade.color.WHITE_SMOKE,
                15,
                anchor_x="center",
                anchor_y="bottom",
            )
        arcade.draw_text(
            f"Round: {self.round_number}",
            self.width // 2,
            self.height - 60,
            arcade.color.WHITE_SMOKE,
            30,
            anchor_x="center",
            anchor_y="center",
        )

    # Move the preview helper with the mouse if we are placing a tower.
    def on_mouse_motion(self, x, y, dx, dy):
        if self.placing_mode:
            self.preview.position = (x, y)

        self.hovered_tower = None
        for tower in self.towers:
            if tower.collides_with_point((x, y)):
                self.hovered_tower = tower
                break

    # Mouse clicks do different things depending on what the player is doing.
    # They can start placing a tower, open an upgrade menu, or buy and sell towers.
    def on_mouse_press(self, x, y, button, modifiers):
        if self.game_state == "menu":
            if button == arcade.MOUSE_BUTTON_LEFT:
                left, bottom, width, height = self.get_menu_button_rect()
                if left <= x <= left + width and bottom <= y <= bottom + height:
                    self.reset_game()
                    self.game_state = "playing"
            return

        COIN_SOUND = arcade.load_sound("ksjsbwuil-cash-register-1-513922.mp3")
        if button == arcade.MOUSE_BUTTON_LEFT and self.button.collides_with_point((x, y)):
            self.placing_mode = not (self.placing_mode and self.placing_tower_type == "basic")
            self.upgrade_menu_open = False
            self.selected_tower = None
            self.set_preview_for_tower_type("basic")
            if self.placing_mode:
                self.preview.position = (x, y)
            return

        if button == arcade.MOUSE_BUTTON_LEFT and self.cannon_button.collides_with_point((x, y)):
            self.placing_mode = not (self.placing_mode and self.placing_tower_type == "cannon")
            self.upgrade_menu_open = False
            self.selected_tower = None
            self.set_preview_for_tower_type("cannon")
            if self.placing_mode:
                self.preview.position = (x, y)
            return

        if button == arcade.MOUSE_BUTTON_LEFT and self.upgrade_menu_open and self.selected_tower and self.is_click_on_upgrade_button(x, y):
            if self.selected_tower.can_upgrade():
                cost = self.selected_tower.get_upgrade_cost()
                if self.money >= cost:
                    self.money -= cost
                    self.selected_tower.apply_upgrade()
                    self.coin_playback = COIN_SOUND.play()
                else:
                    pass
            return

        if button == arcade.MOUSE_BUTTON_LEFT and self.upgrade_menu_open and self.selected_tower and self.is_click_on_sell_button(x, y):
            sell_value = self.selected_tower.get_sell_value()
            self.money += sell_value
            self.towers.remove(self.selected_tower)
            self.selected_tower = None
            self.upgrade_menu_open = False
            self.hovered_tower = None
            self.coin_playback = COIN_SOUND.play()
            return

        if not self.placing_mode:
            if button == arcade.MOUSE_BUTTON_LEFT:
                selected_tower = None
                for tower in self.towers:
                    if tower.collides_with_point((x, y)):
                        selected_tower = tower
                        break
                if selected_tower is not None:
                    self.selected_tower = selected_tower
                    self.upgrade_menu_open = True
                else:
                    self.selected_tower = None
                    self.upgrade_menu_open = False
            return

        if button == arcade.MOUSE_BUTTON_LEFT:
            tower_cost = 400 if self.placing_tower_type == "cannon" else 250
            if self.money >= tower_cost:
                tower = Tower(x, y, tower_type=self.placing_tower_type)
                if self.is_position_valid_for_tower(x, y, tower_type=self.placing_tower_type, sprite=tower):
                    self.towers.append(tower)
                    self.money -= tower_cost
                    self.coin_playback = COIN_SOUND.play()
                    self.placing_mode = False
            else:
                pass

    def on_key_press(self, key, modifiers):
        if self.game_state == "menu":
            if key == arcade.key.SPACE or key == arcade.key.ENTER:
                self.reset_game()
                self.game_state = "playing"

    # Find the enemy in range that is closest to the goal.
    # Towers care more about enemies that are almost at the end than enemies that are far away.
    def get_nearest_enemy(self, sprite):
        if len(self.enemies) == 0:
            return None

        closest_enemy = None
        closest_goal_distance = None
        closest_tower_distance = None

        for enemy in self.enemies:
            tower_distance = arcade.get_distance_between_sprites(sprite, enemy)
            if tower_distance > sprite.range:
                continue

            goal_distance = enemy.distance_to_goal
            if closest_enemy is None:
                closest_enemy = enemy
                closest_goal_distance = goal_distance
                closest_tower_distance = tower_distance
            elif (
                goal_distance < closest_goal_distance
                or (
                    goal_distance == closest_goal_distance
                    and tower_distance < closest_tower_distance
                )
            ):
                closest_enemy = enemy
                closest_goal_distance = goal_distance
                closest_tower_distance = tower_distance

        return closest_enemy


    # Create a new enemy and send it onto the path.
    # Later rounds may spawn faster or tougher enemies.
    def spawn_enemy(self):
        if not self.path_positions:
            return
        if self.round_number >= 10 and self.spawned_this_round % 7 == 0:
            enemy = TankEnemy(self.path_positions)
        elif self.round_number >= 5 and self.spawned_this_round % 5 == 0:
            enemy = SpeedyEnemy(self.path_positions)
        elif self.round_number >= 7 and self.spawned_this_round % 3 == 0:
            enemy = CoolEnemy(self.path_positions)
        else:
            enemy = Enemy(self.path_positions)
        # Scale enemy health with the current round (makes later rounds harder)
        if self.round_number >= 10:
            health_scale = (self.round_number - 10)
            enemy.health = max(1, int(enemy.health + health_scale))
        self.enemies.append(enemy)
        self.spawned_this_round += 1

    # Update the whole game many times every second.
    # This moves enemies, fires towers, checks for hits, and starts the next round.
    def on_update(self, delta_time):
        if self.game_state == "menu":
            return

        self.spawn_timer += delta_time
        if self.spawned_this_round < self.enemies_to_spawn and self.spawn_timer >= self.round_spawn_interval:
            self.spawn_timer -= self.round_spawn_interval
            self.spawn_enemy()

        if self.spawned_this_round >= self.enemies_to_spawn and len(self.enemies) == 0:
            self.round_number += 1
            self.start_round()

        # Move each enemy and end the game if one reaches the end of the path.
        for enemy in list(self.enemies):
            enemy.update(delta_time)
            if enemy.current_target >= len(enemy.path_points):
                self.update_high_score()
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

        # Make each tower look for a target and shoot if it can.
        for tower in self.towers:
            target = self.get_nearest_enemy(tower)
            if target:
                dx = target.center_x - tower.center_x
                dy = target.center_y - tower.center_y
                angle = 270 - math.degrees(math.atan2(dy, dx))
                tower.angle = angle % 360
                tower.time_since_last_shot += delta_time
                if tower.time_since_last_shot >= tower.shoot_interval:
                    tower.time_since_last_shot -= tower.shoot_interval
                    distance = math.hypot(dx, dy)
                    if distance > 0:
                        direction_x = dx / distance
                        direction_y = dy / distance
                        bullet_speed = 640
                        bullet_scale = 1.5 if tower.tower_type == "cannon" else 1
                        bullet = Bullet(
                            tower.center_x,
                            tower.center_y,
                            direction_x * bullet_speed,
                            direction_y * bullet_speed,
                            tower.damage,
                            scale=bullet_scale,
                        )
                        self.bullets.append(bullet)

        # If a bullet hits an enemy, make the enemy lose health.
        for bullet in list(self.bullets):
            enemies_hit = arcade.check_for_collision_with_list(bullet, self.enemies)
            for enemy in enemies_hit:
                if bullet in self.bullets:
                    self.bullets.remove(bullet)
                enemy.health -= bullet.damage
                if enemy.health <= 0 and enemy in self.enemies:
                    self.enemies.remove(enemy)
                    self.money += self.money_given_per_enemy
                break

def main():
    TowerDefense()
    arcade.run()


if __name__ == "__main__":
    main()