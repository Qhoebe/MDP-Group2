import time
import requests
import json
from flask import Flask, request,render_template,url_for,redirect
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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

@app.route('/new')
def new():
    return render_template('new.html')

@app.route('/simulator')
def simulator():
    return render_template('simulator.html',obstacles = obstacles, robot=robot,path=path,commands=commands,position = position)

@app.route('/add/robot',methods=['POST'])
def set_robot():
    global path
    global commands
    global position
    global robot
    x = int(request.form.get('x'))
    y = int(request.form.get('y'))
    direction = int(request.form.get('direction'))
    robot = {'x':x,'y':y,'d':direction,'s':-1}
    # reset grid. 
    commands = []
    path = []
    position = 0
    return redirect(url_for('simulator'))


@app.route('/add/obstacle', methods=['POST'])
def add_obstacle():
    global path
    global commands
    global position
    x = int(request.form.get('x'))
    y = int(request.form.get('y'))
    direction = int(request.form.get('direction'))
    obstacle = {'x': x, 'y':y, 'd':direction}
    if is_unique_obstacle(obstacle, obstacles):
        obstacles.append(obstacle)
        # reset grid. 
        commands = []
        path = []
        position = 0

    return redirect(url_for('simulator'))

def is_unique_obstacle(obstacle,obstacles):
    for obs in obstacles: 
        if obs['y'] == obstacle['y'] and obs['x'] == obstacle['x']:
            return False
    return True

@app.route('/delete/obstacle/<obstacle_json>')
def delete_obstacle(obstacle_json):
    global path
    global commands
    global position
    obstacle = json.loads(obstacle_json)
    if obstacle in obstacles: 
        obstacles.remove(obstacle)
        # reset path
        path = []
        commands = []
        position = 0
    return redirect(url_for('simulator'))

@app.route('/reset/robot')
def reset_robot():
    global robot
    global path
    global commands
    global position
    robot = default_robot
    # reset path
    path = []
    commands = []
    position = 0
    return redirect(url_for('simulator'))

@app.route('/reset/obstacles')
def reset_obstacles():
    global path
    global commands
    global position
    global obstacles
    obstacles = []
    # reset path
    path = []
    commands = []
    position = 0
    return redirect(url_for('simulator'))

@app.route('/reset/all')
def reset_all():
    global robot
    global path
    global commands
    global position
    global obstacles
    robot = default_robot
    obstacles = []
    # reset path
    path = []
    commands = []
    position = 0
    return redirect(url_for('simulator'))


@app.route('/prev_step')
def prev_step():
    global robot
    global position
    if position > 0: 
        position -= 1
        robot = path[position]
    return redirect(url_for('simulator'))

@app.route('/next_step')
def next_step():
    global robot
    global position
    if position < len(path): 
        position += 1
        robot = path[position]
    return redirect(url_for('simulator'))

@app.route('/shortestpath')
def shortest_path():
    global position
    global path
    global commands
    global robot

    # create request json
    details = {}
    details['robot_x'] = robot['x']
    details['robot_y'] = robot['y']
    details['robot_dir'] = robot['d']
    details['retrying'] = True
    details['obstacles'] = obstacles.copy()
    for i in range(len(obstacles)):
       details['obstacles'][i]['id'] = i+1

    # retrieve response
    response = requests.post(" http://127.0.0.1:5001/path", json = details)
        
    result = response.json()

    # update info on simulator
    path = result['data']['path'].copy()
    commands = result['data']['commands_sim'].copy()
    for command in commands: 
        if "SNAP" in command: 
            commands.remove(command)
    commands.insert(0,"ST")
    position = 0
    robot = path[0]
    # display from step 0.
    

    return redirect(url_for('simulator'))

if __name__ == '__main__':
    app.run(port=5100,debug=True)
    
