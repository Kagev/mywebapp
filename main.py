import getpass, json, os, sys, socket, pathlib, logging, threading
from abc import abstractmethod, ABC
from flask import Flask, render_template, request, redirect, abort
from time import time, sleep
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

# lock = RLock()

app = Flask(__name__)

# configured path for files
STATIC_DIR = 'static'
TEMPLATES_DIR = 'templates'
STORAGE_DIR = 'storage'
IMG_DIR = 'img'
DATA_FILE = 'data.json'


#Creat directories if they not found
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)
os.makedirs(STORAGE_DIR, exist_ok=True)
os.makedirs(IMG_DIR, exist_ok=True)

#Main page
@app.route('/')
def home():
    courses = [
        {
            "name": "Python Core",
            "duration": 12,
            "technologies": ["Python", "pip", "OOP", "pickle"]
        },
        {
            "name": "Python Web",
            "duration": 14,
            "technologies": ["Docker", "Poetry", "Pipenv", "SQLAlchemy", "MongoDB", "Django", "FastAPI"]
        },
        {
            "name": "Python Data Science",
            "duration": 12,
            "technologies": ["NumPy", "Pandas", "Matplotlib", "Seaborn", "TensorFlow", "Keras"]
        }
    ]

    return render_template('index.html', courses=courses)


# Page not found "404"
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404


#Message page
@app.route('/message', methods=['GET', 'POST'])
def message():
    if request.method == 'POST':
        username = request.form.get('username')
        message = request.form.get('message')

        # Push data to socket server
        send_data_to_socket(username, message)

        return redirect('/message')
    else:
        return render_template('message.html')


# for send data on Socket Server
def send_data_to_socket(username, message):
    data = {
        "username": username,
        "message": message
    }
    json_data = json.dumps(data).encode("UTF-8")

    socket_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socket_client.sendto(json_data, ("localhost", 5000))
    socket_client.close()

class SocketServer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(("localhost", 5000))
        self.running = True

    def run(self):
        while self.running:
            data, address = self.socket.recvfrom(1024)
            self.process_data(data)

    def process_data(self, data):
        try:
            # decoding
            data_dict = json.loads(data.decode("utf-8"))

            # generation key of datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

            # add data to data.json
            with open(os.path.join(STORAGE_DIR, DATA_FILE), "r+") as file:
                existing_data = json.load(file)
                existing_data[timestamp] = {
                    "username": data_dict.get("username"),
                    "message": data_dict.get("message"),
                }
                file.seek(0)
                json.dump(existing_data, file, indent=4)

        except json.JSONDecodeError:
            print("Error decoding data")

    def stop(self):
        self.running = False
        self.socket.close()


if __name__ == '__main__':
    # Run socket server
    socket_server = SocketServer()
    socket_thread = threading.Thread(target=socket_server.run)
    socket_thread.daemon = True
    socket_thread.start()

    # run app
    app.run(debug=False, host='0.0.0.0', port=3000)
