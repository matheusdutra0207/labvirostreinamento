from is_wire.core import Channel, StatusCode, Status, Logger
from is_wire.rpc import ServiceProvider, LogInterceptor
import time
import random
from is_msgs import common_pb2
from is_msgs.robot_pb2 import RobotTaskRequest
from google.protobuf.empty_pb2 import Empty
from google.protobuf.struct_pb2 import Struct
from is_msgs.common_pb2 import Position
import json

log = Logger(name='Robot')

def brokerAdd():
    config_paht = "config.json"
    fileAdr = open(config_paht, "r")
    brokerAdr = json.load(fileAdr)
    fileAdr.close()
    return brokerAdr["broker_uri"]

class Robot():

    def __init__(self,id ,x ,y ,z):
        self.id = id
        self.position_x = x
        self.position_y = y
        self.position_z = z
   
    def get_id(self):
        return self.id

    def set_position(self, x, y, z):
        self.position_x = x
        self.position_y = y
        self.position_z = z

    def get_position(self):
        return self.position_x, self.position_y, self.position_z

def set_position(idPosition, ctx):
    time.sleep(0.2)

    if idPosition.basic_move_task.positions[0].x < 0 or idPosition.basic_move_task.positions[0].y < 0 or idPosition.basic_move_task.positions[0].z < 0:
        log.error("The number must be positive")
        return Status(StatusCode.OUT_OF_RANGE, "The number must be positive")

    elif idPosition.basic_move_task.positions[0].x > 5 or idPosition.basic_move_task.positions[0].y > 5 or idPosition.basic_move_task.positions[0].z > 5:
        log.error("The number must be less than 5")
        return Status(StatusCode.OUT_OF_RANGE, "The number must be less than 5")

    for robot in robots:
        if robot.id == idPosition.id:
            set_x = idPosition.basic_move_task.positions[0].x
            set_y = idPosition.basic_move_task.positions[0].y
            set_z = idPosition.basic_move_task.positions[0].z
            robot.set_position(set_x, set_y, set_z)
            return Status(StatusCode.OK, why = "Move ok")

def get_position(struct, ctx):
    idPosition = RobotTaskRequest()
    idPosition.id = int(struct.fields["id"].number_value)
    for robot in robots:
        if robot.id == idPosition.id:
            idPosition.basic_move_task.positions.extend([Position(x = 0, y = 0, z = 0)])
            idPosition.basic_move_task.positions[0].x, idPosition.basic_move_task.positions[0].y, idPosition.basic_move_task.positions[0].z = robot.get_position()

    return idPosition

# 3 robots
log.info("Initializing robots ...")
robots = [Robot(1, 2, 3, 1), Robot(2, 1, 1, 1), Robot(3, 2, 2, 2)]

channel = Channel(brokerAdd())
provider = ServiceProvider(channel)

provider.delegate(
    topic="Controller.Get_position",
    function=get_position,
    request_type=Struct,
    reply_type=RobotTaskRequest)

provider.delegate(
    topic="Controller.Set_position",
    function=set_position,
    request_type=RobotTaskRequest,
    reply_type=Empty)

provider.run()