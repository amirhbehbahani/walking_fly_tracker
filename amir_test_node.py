#!/usr/bin/env python
from __future__ import print_function
import Queue
import roslib
import rospy
import numpy

from operator import attrgetter

from multi_tracker.msg import Trackedobject, Trackedobjectlist
from led_scheduler import LedScheduler


class AmirTestNode(object):

    def __init__(self,nodenum=1):

        self.nodenum = str(nodenum)
        rospy.init_node('amir_test')
        self.tracked_objects_sub = rospy.Subscriber('/multi_tracker/' + self.nodenum + '/tracked_objects', Trackedobjectlist, self.tracked_objects_callback)

        self.fly_queue = Queue.Queue()
        self.led_scheduler = LedScheduler()

	self.food_x = 100  # food x coordinate, place holder checked
	self.food_y = 245  # food y coordinate, place holder checked
	self.food_width = 30 # x threshhold, place holder 
	self.food_height = 30 # y threshhold, place holder


    def tracked_objects_callback(self,data):
        number_of_objects = len(data.tracked_objects)
        if number_of_objects > 0: 
            fly = max(data.tracked_objects, key = attrgetter('size'))
	    fly_x, fly_y = numpy.array((fly.position.x, fly.position.y))
            self.fly_queue.put({'x': fly_x, 'y': fly_y})

    def on_food_test(self,fly):
        if abs(fly['x'] - self.food_x) < self.food_width/2.0 and abs(fly['y']- self.food_y) < self.food_height/2.0:
            return True
        else:
            return False

    def run(self):
        while not rospy.is_shutdown():
            fly_on_food = False
            while (self.fly_queue.qsize() > 0):
                fly = self.fly_queue.get()
                fly_on_food = self.on_food_test(fly) or fly_on_food
            self.led_scheduler.update(rospy.Time.now().to_time(), fly_on_food)


        

# -----------------------------------------------------------------------------
if __name__ == '__main__':

    node = AmirTestNode() 
    node.run()

