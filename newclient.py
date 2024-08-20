import socketio

# Create SocketIO
sio = socketio.Client()

#Conection to the server
def main():
    print("Connecting to the chat server...")
    sio.connect('http://localhost:5000')
    print("Connected to the chat server.")

    while True:
        print("\nOptions:")
        print("1. Register User")
        print("2. Authenticate User")
        print("3. Create Group")
        print("4. Send Group Message")
        print("5. Add Group Member")
        print("6. Remove Group Member")
        print("7. Get Chat History")
        print("8. Get Group Chat History")
        print("9. Set User Status")
        print("10. Get User Status")
        print("11. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            username = input("Enter username: ")
            password = input("Enter password: ")
            sio.emit('register', {'username': username, 'password': password})
            sio.sleep(1)  # לתת לשרת זמן לשלוח את התשובה

        elif choice == "2":
            username = input("Enter username: ")
            password = input("Enter password: ")
            sio.emit('login', {'username': username, 'password': password})
            sio.sleep(1)

        elif choice == "3":
            group_name = input("Enter group name: ")
            members = input("Enter group members (comma separated): ").split(',')
            sio.emit('create_group', {'group_name': group_name, 'members': members})
            sio.sleep(1)

        elif choice == "4":
            group_name = input("Enter group name: ")
            message = input("Enter your message: ")
            sio.emit('send_group_message', {'group_name': group_name, 'message': message, 'username': username})
            sio.sleep(1)

        elif choice == "5":
            group_name = input("Enter group name: ")
            new_member = input("Enter new member username: ")
            sio.emit('join_group', {'group_name': group_name, 'username': new_member})
            sio.sleep(1)

        elif choice == "6":
            group_name = input("Enter group name: ")
            member = input("Enter member username to remove: ")
            sio.emit('remove_group_member', {'group_name': group_name, 'member': member})
            sio.sleep(1)

        elif choice == "7":
            user1 = input("Enter your username: ")
            user2 = input("Enter the other username: ")
            sio.emit('get_chat_history', {'user1': user1, 'user2': user2})
            sio.sleep(1)

        elif choice == "8":
            group_name = input("Enter group name: ")
            sio.emit('get_group_chat_history', {'group_name': group_name})
            sio.sleep(1)

        elif choice == "9":
            username = input("Enter your username: ")
            status = input("Enter status (online/offline): ")
            sio.emit('set_user_status', {'username': username, 'status': status})
            sio.sleep(1)

        elif choice == "10":
            username = input("Enter username: ")
            sio.emit('get_user_status', {'username': username})
            sio.sleep(1)

        elif choice == "11":
            print("Exiting...")
            sio.disconnect()
            break

        else:
            print("Invalid option. Please choose a valid option.")

# הפונקציה שתטפל בתשובות מהשרת
@sio.on('register_response')
def on_register_response(data):
    print(f"Register response: {data}")

@sio.on('login_response')
def on_login_response(data):
    print(f"Login response: {data}")

@sio.on('group_message')
def on_group_message(data):
    print(f"New message in {data['group_name']} from {data['sender']}: {data['message']}")

@sio.on('group_chat_history')
def on_group_chat_history(data):
    print(f"Chat history for group {data['group_name']}: {data['history']}")

@sio.on('get_user_status_response')
def on_get_user_status_response(data):
    print(f"Status of {data['username']}: {data['status']}")

if __name__ == '__main__':
    main()
