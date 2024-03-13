import math

class TrackSolver:
    # let 1 = left and 2 = right
    def __init__(
            self,
            radius: float
    ):
        # Initialize a Robot object for robot representation
        self.radius = radius
        self.arrow1 = None
        self.arrow2 = None
        self.distance1 = None
        self.distance2 = None
        self.distance3 = None

    def add_arrow1(self, arrow: int):
        self.arrow1 = arrow

    def add_arrow2(self, arrow: int):
        self.arrow2 = arrow

    def add_distance1(self, distance:float):
        self.distance1 = distance

    def add_distance2(self, distance:float):
        self.distance2 = distance 

    def add_distance3(self, distance:float):
        self.distance3 = distance    

    # path1_d : move to image.
    def calc_path1_d(self):
        commands = []
        distance = self.distance1 - 50 + 15
        commands.insert(0,'FW{}'.format(round(distance)))
        
        return commands
    
    # path1_o : move around obstacle based on image.
    def calc_path1_o(self):
        commands = []
        if(self.arrow1 == 1):
            #go pass obstacle:
            commands.append('FL90')
            commands.append('FR90')
            # turn in:
            commands.append('FR90')
            commands.append('FL90')

        elif (self.arrow1 == 2):
            # go pass obstacle:
            commands.append('FR90')
            commands.append('FL90')
            # turn in:
            commands.append('FL90')
            commands.append('FR90')


        else: 
            return None
        return commands
    
    # path2_d : distance to image.
    def calc_path2_d(self):
        commands = []
        if self.distance2 < 30:
            distance = 30 - self.distance2
            commands.append('BW{}'.format(round(distance)))
        elif self.distance2 > 30: 
            distance = self.distance2 - 30
            commands.append('FW{}'.format(round(distance)))

        return commands

    # path2_o : determine angle to move
    def calc_path2_o(self): 
        commands = []
        if self.arrow2 == 1: 
            commands.append('FL90')

        elif self.arrow2 == 2: 
            commands.append('FR90')
        else:
            return None
        
        return commands
    
    # path3 : determine path over obstacle2
    def calc_path3(self):
        commands = []
        distance = 0
        if self.distance3 == None: 
            return None
        elif self.distance3 > 40:
            distance = self.distance3 - 40
            commands.append('FW{}'.format(round(distance)))
        # check turning.
        if self.arrow2 == 1: 
            commands.append('FR180')
            commands.append('FW{}'.format(round(distance*2 + self.radius) ))
        elif self.arrow2 == 2: 
            commands.append('FL180')
            commands.append('FW{}'.format(round(distance*2 + self.radius) ))
        else: 
            return None
        
        # Add return path
        commands_back = self.calc_pathback(distance)
        if commands_back == None: 
            return None
        else: 
            commands.extend(commands_back)
        return commands
    
    # pathback : calculate path back
    def calc_pathback(self,distance):  
        commands = []
        if(self.arrow2 == 1):
            x = - (self.distance1 + self.distance2 + 85)
            y = self.radius + distance
            d = math.sqrt(x**2 + y**2)
            l = math.sqrt(d**2 - y**2)
            angle = 360 - ((math.atan2(y,x) + math.acos(self.radius/d))/math.pi*180)
            commands.append('FR{}'.format(round(angle)))
            commands.append('FW{}'.format(round(l)))

        elif (self.arrow2 == 2):
            x = - (self.distance1 + self.distance2 + 85)
            y = - (self.radius + distance)
            d = math.sqrt(x**2 + y**2)
            l = math.sqrt(d**2 - y**2)
            angle = 360 + ((math.atan2(y,x) - math.acos(self.radius/d))/math.pi*180)
            commands.append('FL{}'.format(round(angle)))
            commands.append('FW{}'.format(round(l)))

        else: 
            return None
        return commands

        
    
    # # move to image
    # def calc_path2(self):
    #     if(self.arrow1 == 1):
    #         return self.calc_path2_left()
    #     elif (self.arrow1 == 2):
    #         return self.calc_path2_right()
    #     else:
    #         return None
        
    # def calc_path2_left(self):
    #     commands = []
    #     if(self.arrow2 == 1):
    #         distance = self.distance2 - 40 + 15
    #         commands.append('FW{}'.format(round(distance)))
    #         commands.append('FL60')
    #         commands.append('FR60')

    #     elif (self.arrow2 == 2):
    #         x = self.distance2 + 15 + 5
    #         y = - self.radius
    #         d = math.sqrt(x**2 + y**2)
    #         l = math.sqrt(d**2 - (y*2)**2)
    #         angle = 90 - ((math.acos(2*self.radius/d) + math.atan2(y,x)) / math.pi * 180)
    #         commands.append('FR{}'.format(round(angle)))
    #         commands.append('FW{}'.format(round(l)))
    #         commands.append('FL{}'.format(round(angle)))

    #     else: 
    #         return None
        
    #     commands.extend(self.calc_path3())
    #     return commands

    
    # def calc_path2_right(self):
    #     commands = []
    #     if(self.arrow2 == 1):
    #         x = self.distance2 + 15 + 5
    #         y = self.radius
    #         d = math.sqrt(x**2 + y**2)
    #         l = math.sqrt(d**2 - (y*2)**2)
    #         angle = 90 - ((math.acos(2*self.radius/d) - math.atan2(y,x)) / math.pi * 180)
    #         commands.append('FL{}'.format(round(angle)))
    #         commands.append('FW{}'.format(round(l)))
    #         commands.append('FR{}'.format(round(angle)))

    #     elif (self.arrow2 == 2):
    #         distance = self.distance2 - 40 + 15
    #         commands.append('FW{}'.format(round(distance)))
    #         commands.append('FR60')
    #         commands.append('FL60')

    #     else: 
    #         return None
        
    #     commands.extend(self.calc_path3())
    #     return commands
        
    
    
        