#!/usr/bin/env python

import rospy
from geometry_msgs.msg import PoseStamped
from styx_msgs.msg import Lane, Waypoint

import math

'''
This node will publish waypoints from the car's current position to some `x` distance ahead.

As mentioned in the doc, you should ideally first implement a version which does not care
about traffic lights or obstacles.

Once you have created dbw_node, you will update this node to use the status of traffic lights too.

Please note that our simulator also provides the exact location of traffic lights and their
current status in `/vehicle/traffic_lights` message. You can use this message to build this node
as well as to verify your TL classifier.

TODO (for Yousuf and Aaron): Stopline location for each traffic light.
'''

LOOKAHEAD_WPS = 200 # Number of waypoints we will publish. You can change this number
REFRESH_RATE = 30 # Refresh final waypoints at a rate of 30 Hz


class WaypointUpdater(object):
    def __init__(self):
        # logging
        self.debug = True
        self.logger_filename = '/home/workspace/CarND-Capstone/logger_waypoint_updater.txt'
        self.clear_log()

        self.log("Entered WaypointUpdater")
        rospy.init_node('waypoint_updater')

        rospy.Subscriber('/current_pose', PoseStamped, self.pose_cb)
        rospy.Subscriber('/base_waypoints', Lane, self.waypoints_cb)

        # TODO: Add a subscriber for /traffic_waypoint and /obstacle_waypoint below

        self.final_waypoints_pub = rospy.Publisher('final_waypoints', Lane, queue_size=1)

        # TODO: Add other member variables you need below
        self.current_pose = None
        self.base_waypoints = None

        self.loop()
        
    def loop(self):
        rate = rospy.Rate(REFRESH_RATE)
        while not rospy.is_shutdown():
            if self.current_pose and self.base_waypoints:
                closest_waypoint_idx = 0#self.get_closest_waypoint_idx()
                final_waypoints = self.construct_final_waypoints(closest_waypoint_idx)
                self.final_waypoints_pub.publish(final_waypoints)
            rate.sleep()
            
    def construct_final_waypoints(self, start_idx):
        self.log("Entered construct_final_waypoints")
        end_idx = start_idx + LOOKAHEAD_WPS
        self.log("waypoint range: " + str(start_idx) + ":" + str(end_idx))
        final_waypoints = Lane()
        final_waypoints.header = self.base_waypoints.header
        final_waypoints.waypoints = self.base_waypoints.waypoints[start_idx:end_idx]
        return final_waypoints
        
    def pose_cb(self, msg):
        self.log("Entered pose_cb")
        self.current_pose = msg.pose

    def waypoints_cb(self, waypoints):
        self.log("Entered waypoints_cb")
        if not self.base_waypoints:
          self.base_waypoints = waypoints
          #self.log("waypoints = " + str(waypoints))

    def traffic_cb(self, msg):
        self.log("Entered traffic_cb")
        # TODO: Callback for /traffic_waypoint message. Implement
        pass

    def obstacle_cb(self, msg):
        self.log("Entered obstacle_cb")
        # TODO: Callback for /obstacle_waypoint message. We will implement it later
        pass

    def get_waypoint_velocity(self, waypoint):
        return waypoint.twist.twist.linear.x

    def set_waypoint_velocity(self, waypoints, waypoint, velocity):
        waypoints[waypoint].twist.twist.linear.x = velocity

    def distance(self, waypoints, wp1, wp2):
        dist = 0
        dl = lambda a, b: math.sqrt((a.x-b.x)**2 + (a.y-b.y)**2  + (a.z-b.z)**2)
        for i in range(wp1, wp2+1):
            dist += dl(waypoints[wp1].pose.pose.position, waypoints[i].pose.pose.position)
            wp1 = i
        return dist
        
    def clear_log(self):
        self.log_line = 0
        open(self.logger_filename, 'w').close()
        self.log("Entered clear_log")

    def log(self, msg):
        if self.debug:
          with open(self.logger_filename, 'a') as logfile:
              logfile.write(str(self.log_line) + " " + msg + '\n')
              self.log_line += 1

if __name__ == '__main__':
    try:
        WaypointUpdater()
    except rospy.ROSInterruptException:
        rospy.logerr('Could not start waypoint updater node.')
