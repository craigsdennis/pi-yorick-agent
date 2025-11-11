import threading
import argparse
import os

# Installed in the main packages on the uHandPi it's in common_sdk folder
from common.action_group_controller import ActionGroupController
from common.ros_robot_controller_sdk import Board 
from utils import get_available_action_groups

def run_action_group(actNum):
    print(f"Running action group {actNum}")
    threading.Thread(target=agc.runAction, args=(actNum,)).start()

if __name__ == "__main__":
    available_groups = get_available_action_groups()
    available_str = ", ".join(available_groups) if available_groups else "none found"
    
    parser = argparse.ArgumentParser(description="Run action groups on uHandPi")
    parser.add_argument("action_group", nargs="?", default="left_test", 
                       help=f"Name of the action group to run (default: left_test). Available: {available_str}")
    
    args = parser.parse_args()
    
    board = Board()
    agc = ActionGroupController(board, action_path=os.getcwd())
    run_action_group(args.action_group)
