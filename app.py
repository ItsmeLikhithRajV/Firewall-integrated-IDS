from flask import Flask, request, jsonify, render_template, abort
import json
import os
import datetime

app = Flask(__name__, static_folder='static', template_folder='templates')
LOG_FILE = 'access_logs.json'
BLOCK_LIST_FILE = 'block_list.json'

def initialize_logs():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'w') as f:
            json.dump([], f, indent=4)
    if not os.path.exists(BLOCK_LIST_FILE):
        with open(BLOCK_LIST_FILE, 'w') as f:
            json.dump([], f, indent=4)

def read_logs(log_file):
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            return json.load(f)
    return []

def write_logs(log_file, logs):
    with open(log_file, 'w') as f:
        json.dump(logs, f, indent=4)

def read_block_list():
    return read_logs(BLOCK_LIST_FILE)

def write_block_list(block_list):
    write_logs(BLOCK_LIST_FILE, block_list)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/apply_rule', methods=['POST'])
def apply_rule():
    data = request.json
    ip = data.get('ip')
    action = data.get('action')
    if not ip or not action:
        return jsonify({'status': 'error', 'message': 'IP and action are required'}), 400
    
    logs = read_logs(LOG_FILE)
    timestamp = datetime.datetime.now().isoformat()
    logs.append({'ip': ip, 'action': action, 'timestamp': timestamp})
    write_logs(LOG_FILE, logs)

    block_list = read_block_list()
    if action == 'block':
        block_list.append(ip)
    else:
        if ip in block_list:
            block_list.remove(ip)
    write_block_list(block_list)
    return jsonify({'status': 'success'})

@app.route('/get_logs', methods=['GET'])
def get_logs():
    logs = read_logs(LOG_FILE)
    return jsonify(logs)

@app.route('/clear_logs', methods=['POST'])
def clear_logs():
    write_logs(LOG_FILE, [])
    return jsonify({'status': 'success'})

@app.route('/alert', methods=['POST'])
def alert():
    data = request.json
    ip = data.get('ip')
    action = data.get('action')
    if not ip or not action:
        return jsonify({'status': 'error', 'message': 'IP and action are required'}), 400
    
    print(f'Alert: {action} action detected for IP {ip}')
    return jsonify({'status': 'alert logged'})

@app.before_request
def check_ip_block():
    ip = request.remote_addr
    block_list = read_block_list()
    if ip in block_list:
        abort(403)  # Forbidden access

    if ip:
        logs = read_logs(LOG_FILE)
        timestamp = datetime.datetime.now().isoformat()
        logs.append({'ip': ip, 'action': 'access', 'timestamp': timestamp})
        write_logs(LOG_FILE, logs)

if __name__ == '__main__':
    initialize_logs()
    app.run(debug=True)
