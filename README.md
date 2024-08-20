# GroupChatManager

**GroupChatManager** is a chat project designed to support group chat and private conversations between users. The project includes a server based on Flask with Socket.IO support for real-time communication and a client using Socket.IO to interact with the server.

## Key Features

- **Group Chat Management**: Create, manage, add, and remove members from chat groups.
- **Send Group Messages**: Send and receive messages to and from all group members.
- **Chat History**: Store and retrieve private and group chat history.
- **User Authentication**: Register, log in, and manage user statuses (online or offline).
- **Password Hashing**: Secure password storage using bcrypt.
- **Real-time Support**: Real-time communication between client and server using Socket.IO.

## Installation

1. **Install Dependencies**

   Make sure you have Python installed. Then, install the required dependencies by running:

   ```bash
   pip install flask flask-socketio bcrypt
