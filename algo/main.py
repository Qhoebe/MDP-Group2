import time
from algo import MazeSolver 
from helper import command_generator

details = {
    "robot_x": 1,
    "robot_y": 1,
    "robot_dir": 0,
    "retrying": True,
    "obstacles": [
        {
            "x": 12,
            "y": 15,
            "id": 1,
            "d": 2
        },
        {
            "x": 17,
            "y": 9,
            "id": 2,
            "d": 0
        },
        {
            "x": 7,
            "y": 9,
            "id": 3,
            "d": 6
        },
        {
            "x": 6,
            "y": 15,
            "id": 4,
            "d": 0
        },
        {
            "x": 8,
            "y": 14,
            "id": 5,
            "d": 4
        }
    ]
}

def path_finding(details):
    """
    This is the main endpoint for the path finding algorithm
    :return: a json object with a key "data" and value a dictionary with keys "distance", "path", and "commands"
    """
    # Get the json data from the request
    content = details #request.json

    # Get the obstacles, big_turn, retrying, robot_x, robot_y, and robot_direction from the json data
    obstacles = content['obstacles']
    # big_turn = int(content['big_turn'])
    retrying = content['retrying']
    robot_x, robot_y = content['robot_x'], content['robot_y']
    robot_direction = int(content['robot_dir'])

    # Initialize MazeSolver object with robot size of 20x20, bottom left corner of robot at (1,1), facing north, and whether to use a big turn or not.
    maze_solver = MazeSolver(20, 20, robot_x, robot_y, robot_direction, big_turn=None)

    # Add each obstacle into the MazeSolver. Each obstacle is defined by its x,y positions, its direction, and its id
    for ob in obstacles:
        maze_solver.add_obstacle(ob['x'], ob['y'], ob['d'], ob['id'])

    start = time.time()
    # Get shortest path
    optimal_path, distance = maze_solver.get_optimal_order_dp(retrying=retrying)
    print(f"Time taken to find shortest path using A* search: {time.time() - start}s")
    print(f"Distance to travel: {distance} units")
    
    # Based on the shortest path, generate commands for the robot
    commands = command_generator(optimal_path, obstacles)

    # Get the starting location and add it to path_results
    path_results = [optimal_path[0].get_dict()]
    # Process each command individually and append the location the robot should be after executing that command to path_results
    i = 0
    for command in commands:
        if command.startswith("SNAP"):
            continue
        if command.startswith("FIN"):
            continue
        elif command.startswith("FW") or command.startswith("FS"):
            i += int(command[2:]) // 10
        elif command.startswith("BW") or command.startswith("BS"):
            i += int(command[2:]) // 10
        else:
            i += 1
        path_results.append(optimal_path[i].get_dict())
    print(distance)
    print(path_results)
    print(commands)
    return{
        "data": {
            'distance': distance,
            'path': path_results,
            'commands': commands
        },
        "error": None
    }

path_finding(details)