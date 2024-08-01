import socket
import pickle
import struct
import threading
import cv2

clients = {}
client_counter = 1
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host_ip = socket.gethostbyname(socket.gethostname())
port = 16784
socket_address = (host_ip, port)
server_socket.bind(socket_address)
server_socket.listen(5)

def handle_client(client_socket, client_number):
    print(f"Client {client_number} connected.")
    choice = client_socket.recv(1024).decode()

    if choice == '1':
        start_chat(client_socket, client_number)
    elif choice == '2':
        clients[client_number] = client_socket
        receive_and_broadcast_frames(client_socket, client_number)
    elif choice == '3':
        start_video_conferencing(client_socket, client_number)

def start_chat(client_socket, client_number):
    print(f"Chat mode activated for Client {client_number}.")
    print(f"Type 'exit' to end the chat.")
    while True:
        message = client_socket.recv(1024).decode()
        print(f'Client {client_number}: {message}')

        if message.lower() == 'exit':
            break

        send_to_other_clients(client_number, message)

def send_to_other_clients(sender_client_number, message):
    for client_num, client_sock in clients.items():
        if client_num != sender_client_number:
            try:
                client_sock.send(message.encode())
            except:
                print(f"Error sending message to Client {client_num}")

def receive_and_broadcast_frames(client_socket, client_number):
    print(f"Video streaming mode activated for Client {client_number}.")

    try:
        while True:
            payload_size = struct.unpack("!Q", client_socket.recv(8))[0]
            payload = b""
            while len(payload) < payload_size:
                remaining_size = payload_size - len(payload)
                payload += client_socket.recv(4096 if remaining_size > 4096 else remaining_size)

            frame_data = pickle.loads(payload)

            # Broadcast the frame to all connected clients
            broadcast_frame(client_number, frame_data)

    except Exception as e:
        print(f"Error in video streaming for Client {client_number}: {e}")

def broadcast_frame(sender_client_number, frame):
    try:
        frame_data = pickle.dumps(frame, protocol=4)  # Use the highest protocol for better performance
        payload_size = struct.pack("!Q", len(frame_data))
        payload = payload_size + frame_data

        for client_num, client_sock in clients.items():
            if client_num != sender_client_number:
                try:
                    client_sock.sendall(payload)
                except Exception as e:
                    print(f"Error broadcasting frame to Client {client_num}: {e}")

    except Exception as e:
        print(f"Error broadcasting frame: {e}")

def start_video_conferencing(client_socket, client_number):
    print(f"Video streaming mode activated for Client {client_number}.")
    receive_and_broadcast_frames(client_socket, client_number)

def start_server():
    print('Server is listening...', socket.gethostbyname(socket.gethostname()))

    while True:
        client_socket, addr = server_socket.accept()
        global client_counter
        client_handler = threading.Thread(target=handle_client, args=(client_socket, client_counter))
        client_handler.start()
        clients[client_counter] = client_socket
        client_counter += 1

if __name__ == "__main__":
    start_server()
