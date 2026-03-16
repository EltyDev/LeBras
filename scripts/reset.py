from lerobot.robots.so_follower import SO101Follower, SO101FollowerConfig

port_input = input("Write port: ")

robot = SO101Follower(config=SO101FollowerConfig(
    port=port_input,
    id="follower-1"
))

robot.connect()
robot.bus.disable_torque()
robot.disconnect()