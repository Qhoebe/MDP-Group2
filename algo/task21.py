import math
class TrackSolver1:
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
            #assumption sensor at the front of car
            commands.append('FL60')
            commands.append('FR60')

        elif (self.arrow1 == 2):
            commands.append('FR60')
            commands.append('FL60')

        else: 
            return None

        distance = self.distance1 - 40 + 15
        commands.insert(0,'FW{}'.format(round(distance)))
        
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
        #centre of 1st circle is (0,0)
        #centre of 2nd circle is (distance2-40, 25)
        #find distance between centre of 2 circles, R
        distanceR = math.sqrt((self.distance2-40)**2 + 25**2)

        if(self.arrow2 == 1):
            degreeBeta = (math.acos(50/distanceR))/math.pi * 180
            degreeAlpha = (math.asin(25/distanceR))/math.pi * 180
            degreeFi = 90 - degreeBeta - degreeAlpha 
            distanceL = math.sqrt(distanceR**2 -50**2)
            commands.append('FR{}'.format(round(degreeFi)))
            commands.append('FW{}'.format(round(distanceL)))
            commands.append('FL{}'.format(round(degreeFi)))
            commands.append('FL90')
            commands.append('FR90')

        elif (self.arrow2 == 2):
            degreeLeftRight = (math.atan(25/distanceR))/math.pi * 180
            commands.append('FR{}'.format(round(degreeLeftRight)))
            commands.append('FW{}'.format(round(distanceR)))
            commands.append('FR{}'.format(round(90-degreeLeftRight)))
            commands.append('FL90')

        else: 
            return None
        
        commands.extend(self.calc_path3())
        return commands

    
    def calc_path2_right(self):
        commands = []
        distanceR = math.sqrt((self.distance2-40)**2 + 25**2)
        if(self.arrow2 == 1):
            degreeRightLeft = (math.atan(25/distanceR))/math.pi * 180
            degreeBeta = 90 - degreeRightLeft
            commands.append('FL{}'.format(round(degreeRightLeft)))
            commands.append('FW{}'.format(round(distanceR)))
            commands.append('FL{}'.format(round(degreeBeta)))
            commands.append('FR90')

        elif (self.arrow2 == 2):
            degreeAlpha = (math.asin(25/distanceR))/math.pi * 180
            degreeBeta1 = (math.acos(50/distanceR))/math.pi * 180 
            degreeFi = 90 - degreeAlpha - degreeBeta1
            distanceL = math.sqrt(distanceR**2 - 50**2)
            commands.append('FL{}'.format(round(degreeFi)))
            commands.append('FW{}'.format(round(distanceL)))
            commands.append('FR{}'.format(round(degreeFi)))
            commands.append('FR90')
            commands.append('FL90')

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
            commands.append('FR{}'.format(round(angle)))
            commands.append('FW{}'.format(round(l)))

        elif (self.arrow2 == 2):
            x = - (self.distance1 + self.distance2 + 40)
            y = - self.radius
            d = math.sqrt(x**2 + y**2)
            l = math.sqrt(d**2 - y**2)
            angle = 360 + ((math.atan2(y,x) - math.acos(self.radius/d))/math.pi*180)
            commands.append('FL{}'.format(90))
            commands.append('FW{}'.format(50))
            commands.append('FL{}'.format(round(angle)))
            commands.append('FW{}'.format(round(l)))

        else: 
            return None
        return commands

    
        

            
