import time
from algo import MazeSolver 
from task2 import TrackSolver
#from task21 import TrackSolver1
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

    content["robot_x"] = 1
    content["robot_y"] = 2
    content["robot_dir"] = 0
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

# task2

solver = TrackSolver(25)
#solver = TrackSolver1(25)

@app.route('/route1', methods=['POST'])
def task2_route1():
    global solver
    # get request content
    content = request.json

    # calculate path and provide commands
    solver.add_arrow1(content['arrow1'])
    solver.add_distance1(content['distance1'])
    commands = solver.calc_path1()
    if commands is None: 
        error = True
    else: 
        error = False
    
    print(commands)
    return jsonify({'commands':commands,
                    'error':error})


@app.route('/route2', methods=['POST'])
def task2_route2():
    global solver
    # get request content
    content = request.json

    # calculate path and provide commands
    solver.add_arrow2(content['arrow2'])
    solver.add_distance2(content['distance2'])
    commands = solver.calc_path2()
    if commands is None: 
        error = True
    else: 
        error = False
    
    print(commands)
    return jsonify({'commands':commands,
                    'error':error})

@app.route('/path1_d', methods=['POST'])
def task2_path1_d():
    global solver
    # get request content
    content = request.json

    # calculate path and provide commands
    solver.add_distance1(content['distance1'])
    commands = solver.calc_path1_d()
    if commands is None: 
        error = True
    else: 
        error = False
    
    print(commands)
    return jsonify({'commands':commands,
                    'error':error})


@app.route('/path1_o', methods=['POST'])
def task2_path1_o():
    global solver
    # get request content
    content = request.json

    # calculate path and provide commands
    solver.add_arrow1(content['arrow1'])
    commands = solver.calc_path1_o()
    if commands is None: 
        error = True
    else: 
        error = False
    
    print(commands)
    return jsonify({'commands':commands,
                    'error':error})

@app.route('/path2_d', methods=['POST'])
def task2_path2_d():
    global solver
    # get request content
    content = request.json

    # calculate path and provide commands
    solver.add_distance2(content['distance2'])
    commands = solver.calc_path2_d()
    if commands is None: 
        error = True
    else: 
        error = False
    
    print(commands)
    return jsonify({'commands':commands,
                    'error':error})


@app.route('/path2_o', methods=['POST'])
def task2_path2_o():
    global solver
    # get request content
    content = request.json

    # calculate path and provide commands
    solver.add_arrow2(content['arrow2'])
    commands = solver.calc_path2_o()
    if commands is None: 
        error = True
    else: 
        error = False
    
    print(commands)
    return jsonify({'commands':commands,
                    'error':error})

@app.route('/path3', methods=['POST'])
def task3_path3():
    global solver
    # get request content
    content = request.json

    # calculate path and provide commands
    solver.add_distance3(content['distance3'])
    commands = solver.calc_path3()
    if commands is None: 
        error = True
    else: 
        error = False
    
    print(commands)
    return jsonify({'commands':commands,
                    'error':error})



if __name__ == '__main__':
    app.run(port=5001,debug=True)

    # prepare task_2
    


