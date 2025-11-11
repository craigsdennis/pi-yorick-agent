import os
import random
import threading

# Installed in the main packages on the uHandPi it's in common_sdk folder
from common.action_group_controller import ActionGroupController
from common.ros_robot_controller_sdk import Board 

import utils


board = Board()
agc = ActionGroupController(board, action_path=os.getcwd())

random_actions = list(filter(
    lambda group: group.starts_with("random-"), 
    utils.get_available_action_groups()
))

def move_randomly():
    actNum = random.choice(random_actions)
    threading.Thread(target=agc.runAction, args=(actNum,)).start()
