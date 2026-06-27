import arcade

# A tower is a thing we put on the screen to help defend the path.
class Tower(arcade.Sprite):
    def __init__(self, x, y):
        # Use the picture place.png for the tower.
        super().__init__("place.png")
        # Put the tower where the mouse clicked.
        self.position = (x, y)
        # Keep the tower at normal size.
        self.scale = 1


# This is the game window where the path and towers are shown.
class TowerDefense(arcade.Window):

    def __init__(self):
        # Make a window that is 1500 pixels wide and 800 pixels tall.
        super().__init__(1500,800,("accurate defense simulator"))

        # Set the background to brown dirt color.
        arcade.set_background_color(arcade.color.DIRT)

        # Lists to keep track of path pieces, towers, and UI buttons.
        self.paths = arcade.SpriteList()
        self.towers = arcade.SpriteList()
        self.buttons = arcade.SpriteList()
        self.placing_mode = False

        # Preview sprite while in placing mode.
        self.preview = arcade.Sprite("place.png")
        self.preview.scale = 1
        self.preview.alpha = 120
        self.preview.color = arcade.color.WHITE
        self.preview.position = (0, 0)

        # Button to toggle placing mode.
        self.button_texture = arcade.load_texture("mutton.png")
        self.button_exit_texture = arcade.load_texture("exit.png")
        self.button = arcade.Sprite("mutton.png")
        self.button.scale = 1
        self.button.position = (50, 50)
        self.buttons.append(self.button)

        # Start the path at the top-left area.
        self.pathx = 50
        self.pathy = 650
        self.money = 500

        # Add straight path pieces.
        def Path(repeat, angle2set):
            for i in range(repeat):
                path = arcade.Sprite("gerade.png")
                path.scale = 2
                path.position = (self.pathx, self.pathy)
                path.angle = angle2set
                # Move the next path piece to the right place.
                if angle2set == 0:
                    self.pathx += 100
                elif angle2set == 90:
                    self.pathy += 100
                elif angle2set == 180:
                    self.pathx -= 100
                elif angle2set == 270:
                    self.pathy -= 100
                self.paths.append(path)

        # Add a curved path piece.
        def Curve(angle, adjustposition):
            path = arcade.Sprite("curve.png")
            path.scale = 2
            path.position = (self.pathx, self.pathy)
            path.angle = angle
            # Move after placing the curve.
            if adjustposition == 1:
                self.pathx += 100
            elif adjustposition == 2:
                self.pathy += 100
            elif adjustposition == 3:
                self.pathx -= 100
            elif adjustposition == 4:
                self.pathy -= 100
            self.paths.append(path)

        # Create the path shape using straight and curved pieces.
        Path(4,0)
        Curve(270,4)
        Path(2,270)
        Curve(90,1)
        Path(4,0)
        Curve(0,2)
        Path(3,90)
        Curve(180,1)
        Path(1,0)
        Curve(270,4)
        Path(6,270)
        Curve(90,1)
        Path(1,0)
        Curve(0,2)
        Curve(180,1)
        Path(1,0)





        
        

    # Draw the game screen each time it updates.
    def on_draw(self):
        self.clear()
        self.paths.draw()
        self.towers.draw()
        self.buttons.draw()

        if self.placing_mode:
            self.button.texture = self.button_exit_texture
            self.button.position = (50, 50)
            if arcade.check_for_collision_with_list(self.preview, self.paths) or self.money < 250:
                self.preview.color = arcade.color.RED
            else:
                self.preview.color = arcade.color.WHITE
            arcade.draw_sprite(self.preview)
        else:
            self.button.texture = self.button_texture
            self.button.position = (50, 50)

        arcade.draw_text(f"Money: ${self.money}", 10, self.height - 30,
            arcade.color.LAWN_GREEN, 20, anchor_x="left", anchor_y="bottom")

    def on_mouse_motion(self, x, y, dx, dy):
        if self.placing_mode:
            self.preview.position = (x, y)

    def on_mouse_press(self, x, y, button, modifiers):
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
                else:
                    self.towers.append(tower)
                    self.money -= 250
            else:
                print("Not enough money to place a tower!")

# Start the game.
TowerDefense()

arcade.run()