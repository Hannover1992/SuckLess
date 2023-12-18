import socket
import torch
from transformers import pipeline
import soundfile as sf
import sys
from contextlib import contextmanager


# Funktion zur Spracherkennung
def transcribe_audio(pipe, audio_path):
    audio_input, sample_rate = sf.read(audio_path)
    if audio_input.ndim > 1:
        audio_input = audio_input.mean(axis=1)

    chunk_length_s = 30
    chunk_length_samples = chunk_length_s * sample_rate

    gesamter_text = ""
    for start in range(0, len(audio_input), chunk_length_samples):
        end = start + chunk_length_samples
        chunk = audio_input[start:end]
        whisper_input = {"raw": chunk, "sampling_rate": sample_rate}
        prediction = pipe(whisper_input, batch_size=1, return_timestamps=True)["chunks"]
        for chunk in prediction:
            gesamter_text += chunk['text'] + " "
    return gesamter_text

# Hauptfunktion für den Socket-Server
def main():
    device = "cuda:0" if torch.cuda.is_available() else "cpu"

    pipe = pipeline("automatic-speech-recognition", model="openai/whisper-medium", device=device)
    # pipe = pipeline("automatic-speech-recognition", model="openai/whisper-large-v2", device=device)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 5001))
    server_socket.listen(1)
    print("Server listening on port 5001")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr}")

        message = client_socket.recv(1024).decode()
        message = './myrecording.wav'
        if message:
            print("Received audio file path:", message)
            transcribed_text = transcribe_audio(pipe, message)
            with open('out.txt', 'w') as f:
                print(transcribed_text)
                f.write(transcribed_text)
            # Senden des transkribierten Textes an den Client
            client_socket.sendall(transcribed_text.encode())

            client_socket.close()

if __name__ == "__main__":
    main()
