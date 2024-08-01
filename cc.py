import socket
import cv2
import pickle
import struct
import threading
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

data_lock = threading.Lock()
data = 6144
client_number = 0

def start_chat(client_socket):
    print("Chat mode activated.")
    print("Type 'exit' to end the chat.")

    while True:
        sent_message = input('You: ')
        client_socket.send(sent_message.encode())

        if sent_message.lower() == 'exit':
            break

        received_message = client_socket.recv(1024).decode()
        print(f'Server: {received_message}')

        if received_message.lower() == 'exit':
            break

def receive_and_broadcast_frames(client_socket, canvas):
    print("Video streaming mode activated.")

    root = tk.Tk()
    root.title("Video Streaming Client")

    video_frame = ttk.Frame(root)
    video_frame.pack()

    canvas = tk.Canvas(video_frame)
    canvas.pack()

    # Start a separate thread for receiving and displaying frames
    receive_thread = threading.Thread(target=receive_and_display_frames, args=(client_socket, canvas))
    receive_thread.start()

    root.protocol("WM_DELETE_WINDOW", lambda: on_close(root, client_socket))

    root.mainloop()

def receive_and_display_frames(client_socket, canvas):
    try:
        while True:
            payload_size = struct.unpack("!Q", client_socket.recv(8))[0]
            payload = b""
            while len(payload) < payload_size:
                remaining_size = payload_size - len(payload)
                payload += client_socket.recv(4096 if remaining_size > 4096 else remaining_size)

            frame_data = pickle.loads(payload)

            rgb_frame = cv2.cvtColor(frame_data, cv2.COLOR_BGR2RGB)
            photo = ImageTk.PhotoImage(Image.fromarray(rgb_frame))

            canvas.config(width=photo.width(), height=photo.height())
            canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            canvas.image = photo

            canvas.update()
            canvas.after(30)
    except Exception as e:
        print(f"Error in video streaming: {e}")

def on_close(root, client_socket):
    client_socket.send(b'exit_video_conferencing')
    root.destroy()

def start_video_conferencing(client_socket):
    print("Video streaming mode activated.")
    receive_and_broadcast_frames(client_socket)

def start_client():
    global client_number

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host_ip = '172.17.0.153'  # Update with your server's IP address
    port = 16784
    client_socket.connect((host_ip, port))

    print("Connection established.")

    print("Select mode:")
    print("1. Chat")
    print("2. Video Conferencing")
    choice = input("Enter your choice (1 or 2): ")
    client_socket.send(choice.encode())

    if choice == '1':
        start_chat(client_socket)
    elif choice == '2':
        start_video_conferencing(client_socket)

    client_socket.close()

if __name__ == "__main__":
    start_client()
