# module to control mouse using directions and distances
from typing import Tuple

from talon import Context, Module, canvas, cron, ctrl, cron, screen, ui

import math, time

class Eagle:
    def __init__(self, width: float, height: float):
        self.enabled = False
        self.canvas = None
        self.job = None
        self.last_pos = None
        self.width = width
        self.height = height
        self.bearing = -1
        self.distance = 0
        self.max_distance = (self.width ** 2 + self.height ** 2) ** 0.5
        
    def enable(self, bearing = -1):
        self.bearing = bearing
        if self.enabled:
            return
        self.enabled = True
        self.last_pos = ctrl.mouse_pos()        
        
        print("position: {}".format(self.last_pos))
        
        screen = ui.main_screen()
        self.width, self.height = screen.width, screen.height
        self.canvas = canvas.Canvas.from_screen(screen)#  canvas.Canvas(0, 0, self.width, self.height)

        self.canvas.register('mousemove', self.on_mouse)
        self.canvas.register('draw', self.draw_canvas) 
        # self.canvas.freeze() # uncomment this line for debugging
        print("eagle on...")
        print("Eagle position: {}".format(self.last_pos))
        # uncomment this if the mouse movement event isn't working
        #self.job = cron.interval('16ms', self.check_mouse)

        print("self.canvas.rect.width: {}".format(self.canvas.rect.width))
        print("self.canvas.rect.height: {}".format(self.canvas.rect.height))

    def disable(self):
        if not self.enabled:
            return
        cron.cancel(self.job)
        self.enabled = False
        self.canvas.close()
        self.canvas = None

    def pot_of_gold(self,x,y,distance,bearing):
        # calculate next position
        theta = math.radians(bearing)
        x2,y2 = x + distance * math.sin(theta), y - distance * math.cos(theta)
        # make sure it is not off the screen
        # note that the most important equation is :
        # tan(theta) = -dx/dy
        if x2 < 0:
            x2 = 0
            if bearing == 90 or bearing == 270:
                y2 = y
            else:
                y2 = y - (x2 - x) / math.tan(theta)
        if x2 > eagle_object.width - 1:
            x2 = eagle_object.width - 1
            if bearing == 90 or bearing == 270:
                y2 = y
            else:
                y2 = y - (x2 - x) / math.tan(theta)
        if y2 < 0:
            y2 = 0
            x2 = x - (y2 - y) * math.tan(theta)
        if y2 > eagle_object.height - 1:
            y2 = eagle_object.height - 1
            x2 = x - (y2 - y) * math.tan(theta)            
        return x2,y2

    def distance_to_edge(self,x,y,bearing):
        # calculate distance to edge in pixels
        # get math shortcuts
        theta = math.radians(bearing)
        cosine_theta = math.cos(theta)
        sin_theta = math.sin(theta)
        h = eagle_object.height
        w = eagle_object.width
        # get distances in vertical and horizontal directions
        if cosine_theta > 0:
            vertical_distance = y/cosine_theta
        elif cosine_theta < 0:
            vertical_distance = (y-h)/cosine_theta
        else:
            vertical_distance = 9000000
        if sin_theta > 0:
            horizontal_distance = (w-x)/sin_theta
        elif sin_theta < 0:
            horizontal_distance = -x/sin_theta
        else:
            horizontal_distance = 9000000
        # distances minimum of vertical and horizontal distances
        return min(vertical_distance,horizontal_distance)

    def toggle(self):
        if self.enabled:
            self.disable()
        else:
            self.enable()

    def draw_canvas(self, canvas):
        paint = canvas.paint
        paint.antialias = True
        paint.color = 'fff'
        paint.font.size = 36
        
        rect = canvas.rect

        cx, cy = self.last_pos


        def line_aliased(x,y,distance,bearing, color_main = 'ffffff99', color_alias = '00000099'):
            for off, color in ((1, color_alias),(-1, color_alias),(0.5, color_main),(-0.5, color_main),(0, color_main)):
                paint.color = color
                start_x,start_y = self.pot_of_gold(x,y,off,bearing + 90)
                finish_x,finish_y = self.pot_of_gold(start_x,start_y,distance,bearing)
                canvas.draw_line(start_x, start_y, finish_x, finish_y)

        def line_thick_aliased(x,y,distance,bearing, color_main = 'ffffff99', color_alias = '00000099'):
            for off, color in ((1.5, color_alias),(-1.5, color_alias),(1, color_main),(-1, color_main),(0.5, color_main),(-0.5, color_main),(0, color_main)):
                paint.color = color
                start_x,start_y = self.pot_of_gold(x,y,off,bearing + 90)
                finish_x,finish_y = self.pot_of_gold(start_x,start_y,distance,bearing)
                canvas.draw_line(start_x, start_y, finish_x, finish_y)

        def text_aliased(label,x,y,font_size):
                paint.font.size = font_size
                # spine-black and more transparent
                paint.color = '00000077'
                canvas.draw_text(label,x-2,y-2)
                canvas.draw_text(label,x+2,y-2)
                canvas.draw_text(label,x+2,y+2)
                canvas.draw_text(label,x-2,y+2)
                canvas.draw_text(label,x-2,y-1)
                canvas.draw_text(label,x+1,y-1)
                canvas.draw_text(label,x+1,y+1)
                canvas.draw_text(label,x-2,y+1)

                # outline-white and less transparent
                paint.color = 'ffffffee'
                canvas.draw_text(label,x,y)
                canvas.draw_text(label,x+1,y-1)

        def left_cardinal(bearing):
            print(bearing)
            if 45 < bearing <= 135:
                return 'N'
            elif 135 <= bearing <= 225:
                return 'E'
            elif 225 <= bearing <= 315:
                return 'S'
            elif bearing <= 360 and bearing >= 0:
                return 'W'
            else:
                return ''

        def right_cardinal(bearing):
            if 0 <= bearing < 45 or 315 <= bearing <= 360:
                return 'E'
            elif bearing < 135:
                return 'S'
            elif bearing < 225:
                return 'W'
            elif bearing < 315:
                return 'N'
            else:
                return ''

        # get spoke parameters
        distance = 5000
        crosshair_radius = 30
        long_crosshair_length = 12
        short_crosshair_length = 5

        inner_compass_radius = 250
        outer_compass_radius = 200
        short_compass_mark_length = 50
        long_compass_mark_length = 100
        label_offset = 25

        max_distance = self.distance_to_edge(cx,cy,self.bearing)

        # DRAW GRID

        # draw crosshairs around current mouse position
        startBearing = max(0,self.bearing)
        for bearing_adjust in [0,90,180,270]:
            start_x,start_y = self.pot_of_gold(cx,cy,crosshair_radius-long_crosshair_length,startBearing + bearing_adjust)
            line_aliased(start_x, start_y, long_crosshair_length, startBearing + bearing_adjust, color_main = 'ff9999ff', color_alias = 'ffffff99')
        for bearing_adjust in range(0,360,10):
            if not bearing_adjust % 90 == 0:
                start_x,start_y = self.pot_of_gold(cx,cy,crosshair_radius - short_crosshair_length,startBearing + bearing_adjust)
                line_aliased(start_x, start_y, short_crosshair_length, startBearing + bearing_adjust, color_main = 'ff9999ff', color_alias = 'ffffff99')

        
        # bearing not selected
        if self.bearing  == -1:
            # draw diagonals
            for bearing in range(45,359,90):
                start_x,start_y = self.pot_of_gold(cx,cy,crosshair_radius,bearing)
                line_aliased(start_x, start_y, distance, bearing)
            # draw minor spokes
            for bearing in range(0,359,45):
                if bearing % 90 == 0:
                    start_x,start_y = self.pot_of_gold(cx, cy, inner_compass_radius - long_compass_mark_length, bearing)
                    line_aliased(start_x, start_y, long_compass_mark_length, bearing)
            for bearing_x10 in range(0,3590,225):
                bearing = bearing_x10/10
                if bearing % 45 != 0:
                    start_x,start_y = self.pot_of_gold(cx, cy, inner_compass_radius - short_compass_mark_length, bearing)
                    line_aliased(start_x, start_y, short_compass_mark_length, bearing)
            # draw labels for cardinal directions
            paint.color = 'ffffffff'
            for bearing,label in zip([0,90,180,270],['North','East','South','West']):
                start_x,start_y = self.pot_of_gold(cx,cy,inner_compass_radius + label_offset,bearing)
                text_aliased(label,start_x,start_y,45)
            paint.color = 'DDDDDDDD'
            for bearing,label in zip([45,135,225,315],['NE', 'SE','SW','NW']):
                start_x,start_y = self.pot_of_gold(cx,cy,inner_compass_radius + label_offset,bearing)
                text_aliased(label,start_x,start_y,30)
            paint.color = 'BBBBBB99'
            for bearing,label in zip([22.5,67.5,112.5,157.5,202.5,247.5,292.5,337.5],['NNE', 'ENE','ESE','SSE','SSW','WSW','WNW','NNW']):
                start_x,start_y = self.pot_of_gold(cx,cy,inner_compass_radius + label_offset,bearing)
                text_aliased(label,start_x,start_y,18)
                
        # bearing selected
        else:
            # draw selected bearing line            
            start_x,start_y = self.pot_of_gold(cx,cy,10,self.bearing)
            line_thick_aliased(start_x, start_y, distance, self.bearing, color_main = 'ff9999ff', color_alias = 'ffffff99')
                
            # draw bearings thirty degrees on either side
            for left_right in [-1,1]:
                if left_right == -1:
                    cardinal = left_cardinal(self.bearing)
                else:
                    cardinal = right_cardinal(self.bearing)
                # draw full spoke every ten degrees
                for bearing_adjust in [10,20,30]:
                    b = self.bearing + bearing_adjust * left_right
                    start_x,start_y = self.pot_of_gold(cx,cy,100,b)
                    line_aliased(start_x,start_y,distance,b)
                    text_x,text_y = self.pot_of_gold(cx,cy,460,b)
                    label = "{}{}".format(str(abs(bearing_adjust)), cardinal)
                    text_aliased(label,text_x,text_y,18)
                # draw dial marks at two radii
                for bearing_adjust in range(30):
                    if bearing_adjust % 10 != 0:
                        b = self.bearing + bearing_adjust * left_right
                        if bearing_adjust % 5 == 0:
                            extra_length = 7
                        else:
                            extra_length = 0
                        dial_radius = [int(max_distance * x) for x in [0.2,0.5,0.8]]
                        for out_distance in dial_radius:
                            start_x,start_y = self.pot_of_gold(cx,cy,out_distance - extra_length,b)
                            line_aliased(start_x,start_y,20 + extra_length * 2,b)
            
            # draw distance hash lines
            for spacing, size in [(500,60),(100,39),(50,21),(10,12)]:
                for i in range(int(self.max_distance/spacing) + 1):
                    for inout in [-1,1]:
                        d = self.distance + spacing * i * inout
                        if d > 0 and d < max_distance:
                            x,y = self.pot_of_gold(cx,cy,d,self.bearing)
                            sx,sy = self.pot_of_gold(x,y,size/2,self.bearing - 90)
                            if spacing == 10:
                                line_aliased(sx,sy,size,self.bearing + 90)
                            else:
                                line_thick_aliased(sx,sy,size,self.bearing + 90)
                            # draw labels for big lines
                            if spacing == 500 or (spacing == 100 and i % 5 != 0):
                                if 0 < self.bearing < 180:
                                    # draw text to left
                                    sx,sy = self.pot_of_gold(sx,sy,5,self.bearing - 90)
                                else:
                                    sx,sy = self.pot_of_gold(sx,sy,size + 5,self.bearing-90)
                                if spacing == 500:
                                    fs = 27                                
                                else:
                                    fs = 18
                                text_aliased(str(spacing * i),sx,sy,fs)
        
                            
    def on_mouse(self, event):
        # self.check_mouse()
        pass

    def check_mouse(self):
        pos = ctrl.mouse_pos()
        if pos != self.last_pos:
            x, y = pos
            self.canvas.move(x - self.width // 2, y - self.height // 2)
            self.last_pos = pos

eagle_object = Eagle(5000, 5000)
# eagle_object.enable()

mod = Module()
mod.list('compass_cardinal', desc='compass cardinal directions for relative mouse movement')
mod.tag("eagle_showing", desc="Tag indicates whether the eagle compass is showing")


def parse_cardinal(direction: str, distance: int) -> Tuple[bool, int]:
    x, y = ctrl.mouse_pos()
    if ' ' in direction:
        modifier, direction = direction.split(' ', 1)
        if modifier == 'minor':
            distance *= 5
        if modifier == 'major':
            distance *= 25
    if direction == 'left':
        return True, x - distance
    elif direction == 'right':
        return True, x + distance
    elif direction == 'up':
        return False, y - distance
    elif direction == 'down':
        return False, y + distance
    raise ValueError(f"unsupported cardinal direction: {direction}")

@mod.capture(rule="((north | east | south | west | northeast | southeast | southwest | northwest) [(north | east | south | west | northeast | southeast | southwest | northwest)] | up | down | right | left)")
def bearing_capture(m) -> float:
    """determines bearing from spoken compass direction"""
    print('bearing capture, input: {} | length: {}'.format(m,len(m)))
    def bearing_average(b1,b2):
        difference = ((b2 - b1 + 180) % 360) - 180
        return b1 + difference/2
        
    bearing_lookup = {
        'northeast':45,'southeast':135,'southwest':225,'northwest':315,
        'north':0,'east':90,'south':180,'west':270,
        'up':0,'right':90,'down':180,'left':270
        }
    bearing = None
    for w in range(len(m)-1,-1,-1):
        if bearing == None:
            bearing = bearing_lookup[m[w]]
        else:
            bearing = bearing_average(bearing, bearing_lookup[m[w]])
    print("result: {}".format(bearing))
    return bearing
        
@mod.action_class
class Actions:
    def eagle_enable():
        """Enable relative mouse guide"""
        eagle_object.enable()
        ctx.tags = ["user.eagle_showing"]

    def eagle_head_start(bearing: float):
        """enable relative mouse guide and point to given bearing direction"""
        eagle_object.enable(bearing)
        ctx.tags = ["user.eagle_showing"]
        
    def eagle_disable():
        """Disable relative mouse guide"""
        eagle_object.disable()
        ctx.tags = []
        
    def eagle_toggle():
        """Toggle relative mouse guide"""
        eagle_object.toggle()

    def set_cardinal(target: float):
        """set the bearing to a cardinal direction"""
        eagle_object.bearing = target
        print('bearing {}'.format(eagle_object.bearing))

    def move_cardinal(move_degrees: int, target: float):
        """move the bearing direction a certain number of degrees towards a cardinal direction"""
        print('new move cardinal function')
        print("input move_degrees: {}".format(move_degrees))
        print("target: {}".format(target))

        # determine difference between current bearing and target bearing
        delta = (((target - eagle_object.bearing) + 180) % 360) - 180
        
        print("delta: {}".format(delta))

        # limit movement to ensure we don't go past the target direction
        if move_degrees > abs(delta):
            move_degrees = abs(delta)

        print("move_degrees: {}".format(move_degrees))

        # adjust sign of movement if necessary
        if delta < 0:
            move_degrees = -move_degrees
            
        print("move_degrees: {}".format(move_degrees))
            
        # perform movement!
        eagle_object.bearing = (eagle_object.bearing + move_degrees) % 360

        print("result: {}".format(eagle_object.bearing))

    def fly_out(distance: int):
        """move out the specified number of pixels"""
        eagle_object.distance = eagle_object.distance + distance
        cx,cy = eagle_object.last_pos        
        x,y = eagle_object.pot_of_gold(cx, cy, distance, eagle_object.bearing)
        ctrl.mouse_move(x, y)
        eagle_object.distance = 0
        eagle_object.last_pos = x,y

        
        print("function move_out")
        print("distance: {}".format(eagle_object.distance))

    def reverse():
        """reverse direction"""
        print("reverse function")
        eagle_object.bearing = (eagle_object.bearing + 180) % 360        

    def fly_back(distance: int):
        """turn around and move back the specified number of pixels"""
        cx,cy = eagle_object.last_pos        
        reverse_bearing = (eagle_object.bearing + 180) % 360
        x,y = eagle_object.pot_of_gold(cx, cy, distance, reverse_bearing)
        ctrl.mouse_move(x, y)
        eagle_object.distance = 0
        eagle_object.last_pos = x,y
        
    def center_eagle():
        """move mouse to center of screen"""
        x,y = int(eagle_object.width/2), int(eagle_object.height/2)
        ctrl.mouse_move(x,y)
        eagle_object.last_pos = x,y
        eagle_object.enable()
        print(eagle_object)

    def test(d1: float):
        """test function"""
        x = 3

        

ctx = Context()
