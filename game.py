import arcade

class TowerDefense(arcade.Window):

    def __init__(self):
        super().__init__(1900,1100,("accurate defense simulator"))

        arcade.set_background_color(arcade.color.DIRT)

        self.paths = arcade.SpriteList()

        self.pathx = 50
        self.pathy = 1050
        self.current_angle = 0
        def anglecheck():
            if self.current_angle == -270:
                self.current_angle = 90
            if self.current_angle == 270:
                self.current_angle = -90


            if self.current_angle == 0:
                self.pathx = self.pathx + 100
            elif self.current_angle == -90:
                self.pathy = self.pathy - 100
            elif self.current_angle == -180 or self.current_angle == 180:
                self.pathx = self.pathx - 100
            elif self.current_angle == 90:
                self.pathy = self.pathy + 100
        
        def PathCurveGen(repeat, angle2set): #, start_x, start_y):
        
            for i in range(repeat):
                path = arcade.Sprite("schlange/gerade.png")
                path.scale = 2
                path.position = (self.pathx , self.pathy)
                self.paths.append(path)
                path.angle = self.current_angle


                anglecheck()

            path = arcade.Sprite("schlange/curve.png")
            path.scale = 2
            path.position = (self.pathx,self.pathy)
            # if flip == True:
            #     self.current_angle = self.current_angle - 90
            # else:
            #     self.current_angle = self.current_angle
            self.current_angle = self.current_angle + angle2set
            path.angle = self.current_angle
            self.paths.append(path)
            anglecheck()

    
        
        print(self.current_angle)
        PathCurveGen(3,-90)
        print(self.current_angle)
        PathCurveGen(3,180)
        self.current_angle = 0
        print(self.current_angle)
        PathCurveGen(3,0)
        print(self.current_angle)
        PathCurveGen(2,90)
        print(self.current_angle)
        



        
        

    def on_draw(self):
        self.clear()
        self.paths.draw()

TowerDefense()

arcade.run()