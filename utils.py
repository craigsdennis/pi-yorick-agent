import os
import glob
import sqlite3
import random
import uuid

def get_available_action_groups():
    """Get list of available action groups from ./action_groups directory.
    
    Returns:
        list: List of action group names (without .d6a extension)
    """
    pattern = os.path.join("action_groups", "*.d6a")
    files = glob.glob(pattern)
    return [os.path.splitext(os.path.basename(f))[0] for f in files]

def create_random_action_group():
    create_action_group("random-" + str(uuid.uuid4()), [{
        "Time": random.randint(300, 500),
        "Servo1": random.randint(1500, 2200),
        "Servo2": random.randint(1500, 2200),
        "Servo3": random.randint(1500, 2200),
        "Servo4": random.randint(1500, 2200),
        "Servo5": random.randint(1500, 2200),
        "Servo6": random.randint(1400, 1600),
    }])
    

def create_action_group(name, action_steps):
    """Create a new action group SQLite database.
    
    Args:
        name (str): Name of the action group (without .d6a extension)
        action_steps (list): List of dictionaries with Time, Servo1-6 values
        
    Returns:
        dict: Result with success status and message
    """
    if not name or not action_steps:
        return {
            "success": False,
            "message": "Name and action_steps are required"
        }
    
    # Ensure action_groups directory exists
    os.makedirs("action_groups", exist_ok=True)
    
    # Create database file path
    db_path = os.path.join("action_groups", f"{name}.d6a")
    
    try:
        # Create SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create ActionGroup table with the exact schema from the existing code
        cursor.execute("""
            CREATE TABLE ActionGroup(
                [Index] INTEGER PRIMARY KEY AUTOINCREMENT
                NOT NULL ON CONFLICT FAIL
                UNIQUE ON CONFLICT ABORT,
                Time INT,
                Servo1 INT,
                Servo2 INT,
                Servo3 INT,
                Servo4 INT,
                Servo5 INT,
                Servo6 INT
            )
        """)
        
        # Insert action steps using exact values passed in
        for step in action_steps:
            cursor.execute("""
                INSERT INTO ActionGroup (Time, Servo1, Servo2, Servo3, Servo4, Servo5, Servo6)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                step["Time"],
                step["Servo1"],
                step["Servo2"], 
                step["Servo3"],
                step["Servo4"],
                step["Servo5"],
                step["Servo6"]
            ))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": f"Action group '{name}' created successfully with {len(action_steps)} steps",
            "file_path": db_path
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to create action group '{name}': {str(e)}"
        }