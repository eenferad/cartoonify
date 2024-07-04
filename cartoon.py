import cv2
from PIL import Image
import numpy as np
import shutil
import time
from moviepy.editor import VideoFileClip
import threading
import subprocess
import sys
import argparse
from pytube import YouTube, exceptions

# ASCII character set for conversion
ASCII_CHARS = "@%#*+=-:. "

def resize_image(image, new_width, new_height):
    aspect_ratio = image.width / image.height
    terminal_aspect_ratio = 2 * new_width / new_height  # Adjust for terminal character aspect ratio

    if aspect_ratio > terminal_aspect_ratio:
        new_height = int(new_width / aspect_ratio / 2)
    else:
        new_width = int(new_height * aspect_ratio * 2)

    resized_image = image.resize((new_width, new_height))
    return resized_image

def grayify(image):
    grayscale_image = image.convert("L")
    return grayscale_image

def pixels_to_ascii(image):
    pixels = image.getdata()
    ascii_str = ""
    for pixel in pixels:
        ascii_str += ASCII_CHARS[pixel * len(ASCII_CHARS) // 256]
    return ascii_str

def convert_frame_to_ascii(frame, new_width, new_height):
    image = Image.fromarray(frame)
    image = resize_image(image, new_width, new_height)
    image = grayify(image)
    ascii_str = pixels_to_ascii(image)
    img_width = image.width
    ascii_str_len = len(ascii_str)
    ascii_img = ""
    for i in range(0, ascii_str_len, img_width):
        ascii_img += ascii_str[i:i + img_width] + "\n"
    return ascii_img

def play_audio(video_path, stop_event):
    # Use VLC to play the audio and disable video output
    vlc_process = subprocess.Popen(["vlc", "--intf", "dummy", "--no-video", "--play-and-exit", video_path],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        while not stop_event.is_set():
            time.sleep(0.1)
    finally:
        vlc_process.terminate()
        vlc_process.wait()

def play_video_with_audio(video_path):
    video_clip = VideoFileClip(video_path)
    fps = video_clip.fps
    frame_delay = 1 / fps

    stop_event = threading.Event()

    # Start audio playback in a separate thread
    audio_thread = threading.Thread(target=play_audio, args=(video_path, stop_event))
    audio_thread.start()

    cap = cv2.VideoCapture(video_path)

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            columns, rows = shutil.get_terminal_size()
            new_width = columns
            new_height = rows - 1

            ascii_frame = convert_frame_to_ascii(frame, new_width, new_height)
            print(ascii_frame)
            time.sleep(frame_delay)
    except KeyboardInterrupt:
        print("Interrupted by user. Exiting...")
    finally:
        stop_event.set()
        cap.release()
        audio_thread.join()

def download_youtube_video(youtube_url):
    try:
        yt = YouTube(youtube_url)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').first()
        video_path = stream.download()
        return video_path
    except exceptions.AgeRestrictedError:
        print("The video is age-restricted and cannot be accessed without logging in.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Play a local video file or a YouTube video as ASCII art.")
    parser.add_argument("video_path_or_url", help="Path to the local video file or URL of the YouTube video")
    args = parser.parse_args()

    input_path = args.video_path_or_url

    if input_path.startswith("http://") or input_path.startswith("https://"):
        video_path = download_youtube_video(input_path)
    else:
        video_path = input_path

    play_video_with_audio(video_path)
