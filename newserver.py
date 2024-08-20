from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import bcrypt
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

class ChatManager:
    def __init__(self):
        self.group_chats = {}
        self.group_messages = {}
        self.chat_logs = {}
        self.users = {}
        self.user_statuses = {}

    def create_group(self, group_name, group_members):
        if group_name in self.group_chats:
            raise ValueError("Group already exists.")
        self.group_chats[group_name] = group_members
        self.group_messages[group_name] = []

    def send_group_message(self, group_name, message, sender):
        if group_name not in self.group_chats:
            raise ValueError("Group does not exist.")
        if sender not in self.group_chats[group_name]:
            raise ValueError("Sender not in group.")
        
        timestamp = time.time()
        self.group_messages[group_name].append((sender, message, timestamp))
        self.log_group_message(group_name, sender, message, timestamp)

    def add_group_member(self, group_name, new_member):
        if new_member in self.group_chats[group_name]:
            raise ValueError("Member already exists.")
        self.group_chats[group_name].append(new_member)

    def remove_group_member(self, group_name, member):
        if member not in self.group_chats[group_name]:
            raise ValueError("Member does not exist.")
        self.group_chats[group_name].remove(member)

    def log_message(self, sender, recipient, message, timestamp):
        chat_key = tuple(sorted([sender, recipient]))
        if chat_key not in self.chat_logs:
            self.chat_logs[chat_key] = []
        self.chat_logs[chat_key].append((sender, message, timestamp))

    def log_group_message(self, group_name, sender, message, timestamp):
        if group_name not in self.chat_logs:
            self.chat_logs[group_name] = []
        self.chat_logs[group_name].append((sender, message, timestamp))

    def get_chat_history(self, user1, user2):
        chat_key = tuple(sorted([user1, user2]))
        return self.chat_logs.get(chat_key, [])

    def get_group_chat_history(self, group_name):
        return self.chat_logs.get(group_name, [])
    
    def hash_password(self, password):
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
        return password_hash

    def register_user(self, username, password):
        if username in self.users:
            raise ValueError("Username already exists.")
        self.users[username] = {'password': self.hash_password(password), 'status': 'offline'}

    def verify_password(self, stored_password, provided_password):
        return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password)

    def authenticate_user(self, username, password):
        if username not in self.users:
            raise ValueError("User does not exist.")
        return self.verify_password(self.users[username]['password'], password)

    def set_user_status(self, username, status):
        if username not in self.users:
            raise ValueError("User does not exist.")
        self.users[username]['status'] = status

    def get_user_status(self, username):
        if username not in self.users:
            raise ValueError("User does not exist.")
        return self.users[username]['status']

chat_manager = ChatManager()

@socketio.on('register_user')
def handle_register(data):
    username = data['username']
    password = data['password']
    try:
        chat_manager.register_user(username, password)
        emit('register_response', {'status': 'success'})
    except ValueError as e:
        emit('register_response', {'status': 'error', 'message': str(e)})

@socketio.on('authenticate_user')
def handle_login(data):
    username = data['username']
    password = data['password']
    try:
        if chat_manager.authenticate_user(username, password):
            chat_manager.set_user_status(username, 'online')
            emit('login_response', {'status': 'success'})
        else:
            emit('login_response', {'status': 'error', 'message': 'Invalid credentials'})
    except ValueError as e:
        emit('login_response', {'status': 'error', 'message': str(e)})

@socketio.on('create_group')
def handle_create_group(data):
    group_name = data['group_name']
    members = data['members']
    try:
        chat_manager.create_group(group_name, members)
        emit('create_group_response', {'status': 'success'})
    except ValueError as e:
        emit('create_group_response', {'status': 'error', 'message': str(e)})

@socketio.on('join_group')
def handle_join_group(data):
    username = data['username']
    group_name = data['group_name']
    try:
        chat_manager.add_group_member(group_name, username)
        join_room(group_name)
        emit('join_group_response', {'status': 'success'})
    except ValueError as e:
        emit('join_group_response', {'status': 'error', 'message': str(e)})

@socketio.on('send_group_message')
def handle_send_group_message(data):
    username = data['username']
    group_name = data['group_name']
    message = data['message']
    try:
        chat_manager.send_group_message(group_name, message, username)
        emit('group_message', {'group_name': group_name, 'sender': username, 'message': message}, room=group_name)
    except ValueError as e:
        emit('send_group_message_response', {'status': 'error', 'message': str(e)})

@socketio.on('get_group_chat_history')
def handle_get_group_chat_history(data):
    group_name = data['group_name']
    history = chat_manager.get_group_chat_history(group_name)
    emit('group_chat_history', {'group_name': group_name, 'history': history})

@socketio.on('set_user_status')
def handle_set_user_status(data):
    username = data['username']
    status = data['status']
    try:
        chat_manager.set_user_status(username, status)
        emit('set_user_status_response', {'status': 'success'})
    except ValueError as e:
        emit('set_user_status_response', {'status': 'error', 'message': str(e)})

@socketio.on('get_user_status')
def handle_get_user_status(data):
    username = data['username']
    try:
        status = chat_manager.get_user_status(username)
        emit('get_user_status_response', {'status': 'success', 'status_value': status})
    except ValueError as e:
        emit('get_user_status_response', {'status': 'error', 'message': str(e)})

@socketio.on('disconnect')
def handle_disconnect():
    username = request.sid  # This assumes you store the username in the session or similar
    chat_manager.set_user_status(username, 'offline')

if __name__ == '__main__':
    socketio.run(app, debug=True)
