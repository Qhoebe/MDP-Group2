import time
import requests
import json
from algo import MazeSolver 
from helper import command_generator
from flask import Flask, request, jsonify, render_template,url_for,redirect
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
    return jsonify({
        "data": {
            'distance': distance,
            'path': path_results,
            'commands': commands
        },
        "error": None
    })


# Code Section for Simulator

# global variables
Direction = {
  "NORTH": 0,
  "EAST": 2,
  "SOUTH": 4,
  "WEST": 6,
  "SKIP": 8,
}
obstacles = []  # This list will store your obstacles
default_robot = {'x':1,'y':1,'d':0,'s':-1}
robot = {'x':1,'y':1,'d':0,'s':-1}
counter = 0
path = []
commands = []
position = 0

@app.route('/')
def hello():
    return render_template('hello.html')

@app.route('/simulator')
def simulator():
    return render_template('simulator.html',obstacles = obstacles, robot=robot,path=path,commands=commands,position = position)

@app.route('/add/obstacle', methods=['POST'])
def add_obstacle():
    x = request.form.get('x')
    y = request.form.get('y')
    direction = request.form.get('direction')
    obstacle = {'x': x, 'y':y, 'd':direction}
    obstacles.append(obstacle)
    return redirect(url_for('simulator'))

@app.route('/delete/obstacle/<obstacle_json>')
def delete_obstacle(obstacle_json):
    obstacle = json.loads(obstacle_json)
    if obstacle in obstacles: 
        obstacles.remove(obstacle)
        # reset path
        path = []
        commands = []
        position = 0
    return redirect(url_for('simulator'))

@app.route('/prev_step')
def prev_step():
    if position > 0: 
        position -= 1
        robot = path[position]
    return redirect(url_for('simulator'))

@app.route('/next_step')
def next_step():
    if position < len(path): 
        position += 1
        robot = path[position]
    return redirect(url_for('simulator'))

@app.route('/shortestpath')
def shortest_path():
    # create request json
    details = {}
    details['robot_x'] = robot['x']
    details['robot_y'] = robot['y']
    details['robot_dir'] = robot['d']
    details['retrying'] = True
    details['obstacles'] = obstacles.copy()
    for i in range(5):
       details['obstacles'][i]['id'] = id+1

    # retrieve response
    response = requests.post(" http://127.0.0.1:5000/path", json = details)
    result = response.json()

    # update info on simulator
    path = result['path'].copy()
    commands = result['commands'].copy()
    for command in commands: 
        if "SNAP" in command: 
            commands.remove(command)
    position = 0
    robot = path[0]
    # display from step 0.
    

    return redirect(url_for('simulator'))
    









if __name__ == '__main__':
    app.run(debug=True)

    # path_finding(details)

