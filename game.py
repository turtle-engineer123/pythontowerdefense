import arcade

class TowerDefense(arcade.Window):

    def __init__(self):
        super().__init__(1500,800,("accurate defense simulator"))

        arcade.set_background_color(arcade.color.DIRT)

        self.paths = arcade.SpriteList()
        self.pathx = 50
        self.pathy = 650

        def Path(repeat, angle2set):
            for i in range(repeat):
                path = arcade.Sprite("gerade.png")
                path.scale = 2
                path.position = (self.pathx, self.pathy)
                path.angle = angle2set
                if angle2set == 0:
                    self.pathx += 100
                elif angle2set == 90:
                    self.pathy += 100
                elif angle2set == 180:
                    self.pathx -= 100
                elif angle2set == 270:
                    self.pathy -= 100
                self.paths.append(path)

        def Curve(angle, adjustposition):
            path = arcade.Sprite("curve.png")
            path.scale = 2
            path.position = (self.pathx, self.pathy)
            path.angle = angle
            if adjustposition == 1:
                self.pathx += 100
            elif adjustposition == 2:
                self.pathy += 100
            elif adjustposition == 3:
                self.pathx -= 100
            elif adjustposition == 4:
                self.pathy -= 100
            self.paths.append(path)

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





        
        

    def on_draw(self):
        self.clear()
        self.paths.draw()

TowerDefense()

arcade.run()