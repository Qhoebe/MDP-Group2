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

    def add_arrow1(self, arrow: int):
        self.arrow1 = arrow

    def add_arrow2(self, arrow: int):
        self.arrow2 = arrow

    def add_distance1(self, distance:float):
        self.distance1 = distance

    def add_distance2(self, distance:float):
        self.distance2 = distance    
    
    def calc_path1(self):
        commands = []
        if(self.arrow1 == 1):
            #assumption senor at the front of car
            commands.append('FL60')
            commands.append('FR60')

        elif (self.arrow1 == 2):
            commands.append('FR60')
            commands.append('FL60')

        else: 
            return None

        distance = self.distance1 - 40 + 15
        commands.insert(0,'FW{}'.format(distance))
        
        return commands
    
    
    def calc_path2(self):
        if(self.arrow1 == 1):
            return self.calc_path2_left()
        elif (self.arrow1 == 2):
            return self.calc_path2_right()
        else:
            return None
        
    def calc_path2_left(self):
        commands = []
        if(self.arrow2 == 1):
            distance = self.distance2 - 40 + 15
            commands.append('FW{}'.format(distance))
            commands.append('FL60')
            commands.append('FR60')

        elif (self.arrow2 == 2):
            x = self.distance2 + 15 + 5
            y = - self.radius
            d = math.sqrt(x**2 + y**2)
            l = math.sqrt(d**2 - (y*2)**2)
            angle = 90 - ((math.acos(2*self.radius/d) + math.atan2(y,x)) / math.pi * 180)
            commands.append('FR{}'.format(angle))
            commands.append('FW{}'.format(l))
            commands.append('FL{}'.format(angle))

        else: 
            return None
        
        commands.extend(self.calc_path3())
        return commands

    
    def calc_path2_right(self):
        commands = []
        if(self.arrow2 == 1):
            x = self.distance2 + 15 + 5
            y = self.radius
            d = math.sqrt(x**2 + y**2)
            l = math.sqrt(d**2 - (y*2)**2)
            angle = 90 - ((math.acos(2*self.radius/d) - math.atan2(y,x)) / math.pi * 180)
            commands.append('FL{}'.format(angle))
            commands.append('FW{}'.format(l))
            commands.append('FR{}'.format(angle))

        elif (self.arrow2 == 2):
            distance = self.distance2 - 40 + 15
            commands.append('FW{}'.format(distance))
            commands.append('FR60')
            commands.append('FL60')

        else: 
            return None
        
        commands.extend(self.calc_path3())
        return commands
        
    def calc_path3(self):
        commands = []
        if(self.arrow2 == 1):
            x = - (self.distance1 + self.distance2 + 40)
            y = self.radius
            d = math.sqrt(x**2 + y**2)
            l = math.sqrt(d**2 - y**2)
            angle = 360 - ((math.atan2(y,x) + math.acos(self.radius/d))/math.pi*180)
            commands.append('FR{}'.format(90))
            commands.append('FW{}'.format(50))
            commands.append('FR{}'.format(angle))
            commands.append('FW{}'.format(l))

        elif (self.arrow2 == 2):
            x = - (self.distance1 + self.distance2 + 40)
            y = - self.radius
            d = math.sqrt(x**2 + y**2)
            l = math.sqrt(d**2 - y**2)
            angle = 360 + ((math.atan2(y,x) - math.acos(self.radius/d))/math.pi*180)
            commands.append('FL{}'.format(90))
            commands.append('FW{}'.format(50))
            commands.append('FL{}'.format(angle))
            commands.append('FW{}'.format(l))

        else: 
            return None
        return commands

    
        

            


