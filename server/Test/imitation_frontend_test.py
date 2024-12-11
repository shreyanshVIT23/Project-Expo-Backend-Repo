import requests
import pyaudio
import wave
import webbrowser
from test_api import BASE_URL


def record_audio(
    file_name, record_seconds, sample_rate=44100, chunk_size=1024, channels=1
):

    audio = pyaudio.PyAudio()

    stream = audio.open(
        format=pyaudio.paInt16,
        channels=channels,
        rate=sample_rate,
        input=True,
        frames_per_buffer=chunk_size,
    )

    print("Recording...")
    frames = []

    for _ in range(int(sample_rate / chunk_size * record_seconds)):
        data = stream.read(chunk_size)
        frames.append(data)

    print("Recording complete.")

    stream.stop_stream()
    stream.close()
    audio.terminate()

    with wave.open(file_name, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(sample_rate)
        wf.writeframes(b"".join(frames))

    print(f"Audio saved as {file_name}")


def upload_file_to_api(api_url, file_path):

    with open(file_path, "rb") as file:

        files = {"audio_file": file}

        try:

            response = requests.post(api_url, files=files)

            if response.status_code == 200:
                print("File uploaded successfully!")
                print("Server Response:", response.json())
                open_in_browser(response.json())
            else:
                print(f"Failed to upload file. Status Code: {response.status_code}")
                print("Server Response:", response.text)

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")


def open_in_browser(response):
    svg_content = response["files"]

    print(f"Opening start in the default web browser...")
    webbrowser.open(
        f"{BASE_URL}/{svg_content["start_floor"]}",
    )

    print(f"Opening end in the default web browser...")
    webbrowser.open(
        f"{BASE_URL}/{svg_content["end_floor"]}",
    )


if __name__ == "__main__":
    record_audio("example_audio.wav", 10)
    api_endpoint = "http://127.0.0.1:5000/upload"
    file_to_upload = "example_audio.wav"
    upload_file_to_api(api_endpoint, file_to_upload)
