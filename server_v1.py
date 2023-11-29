from flask import Flask, request, jsonify
import socket
import pyaudio
import threading

#%%
app = Flask(__name__)

# Constants
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
HOST = '0.0.0.0'
PORT = 1245

# Initialize PyAudio
audio = pyaudio.PyAudio()
input_stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
output_stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True)
#%%
# Function to send audio to the client
def send_audio_to_client(client_socket):
    while True:
        audio_data = input_stream.read(CHUNK)
        client_socket.sendall(audio_data)

# Function to receive audio from the client
def receive_audio_from_client(client_socket):
    while True:
        data = client_socket.recv(CHUNK)
        output_stream.write(data)

@app.route('/start_audio', methods=['POST'])
def start_audio():
    # Create a socket for communication
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)

    # Accept incoming connections
    print(f"Waiting for a connection on {HOST}:{PORT}")
    client_socket, client_address = server_socket.accept()
    print(f"Connected to {client_address}")

    # Start threads for sending and receiving audio
    send_thread_to_client = threading.Thread(target=send_audio_to_client, args=(client_socket,))
    receive_thread_from_client = threading.Thread(target=receive_audio_from_client, args=(client_socket,))
    
    send_thread_to_client.start()
    receive_thread_from_client.start()

    return jsonify({"status": "Audio streaming started"})
#%%
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, threaded=True)
