import time
from algo import MazeSolver 
from helper import command_generator
from flask import Flask, request, jsonify
from flask_cors import CORS
from entities.Entity import Direction

app = Flask(__name__)
CORS(app)


@app.route('/status', methods=['GET'])
def status():
    """
    This is a health check endpoint to check if the server is running
    :return: a json object with a key "result" and value "ok"
    """
    return jsonify({"result": "ok"})


# Calculating shortest path
@app.route('/path', methods=['POST'])
def path_finding():
    """
    This is the main endpoint for the path finding algorithm
    :return: a json object with a key "data" and value a dictionary with keys "distance", "path", and "commands"
    """
    # Get the json data from the request
    content =  request.json 
    #content =  details
    
    if "robot_x" not in content: 
        content["robot_x"] = 1
    if "robot_y" not in content: 
        content["robot_y"] = 2
    if "robot_dir" not in content:
        content["robot_dir"] = 0
    if "retrying" not in content: 
        content["retrying"] = True

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

    stm_commands = []
    for command in commands:
        if command.startswith("FIN"):
            continue
        stm_commands.append(command)
        stm_commands.append("DL")

    return jsonify({
        "data": {
            'distance': distance,
            'path': path_results,
            'commands': stm_commands,
            'commands_sim': commands
        },
        "error": None
    })


if __name__ == '__main__':
    app.run(port=5001,debug=True)

    



