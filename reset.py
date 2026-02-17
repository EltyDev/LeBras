from lerobot.robots.so_follower import SO101Follower, SO101FollowerConfig

robot = SO101Follower(config=SO101FollowerConfig(
    port="/dev/ttyACM1",
    id="follower-1"
))

robot.connect()
robot.bus.disable_torque()
robot.disconnect()