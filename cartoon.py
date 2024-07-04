import cv2
from PIL import Image
import numpy as np
import shutil
import time
from moviepy.editor import VideoFileClip
import threading

# Erfan ENFERAD
ASCII_CHARS = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/|()1{}[]?-_+~<>i!lI;:,\"^`'. "

def resize_image(image, new_width, new_height):
    
    aspect_ratio = 9 / 16
    terminal_aspect_ratio = new_height / new_width
    
    if terminal_aspect_ratio > aspect_ratio:
        new_height = int(new_width * aspect_ratio)
    else:
        new_width = int(new_height / aspect_ratio)
        
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

def play_video_with_audio(video_path):
    
    video_clip = VideoFileClip(video_path)
    
    
    fps = video_clip.fps
    frame_delay = 1 / fps
    
    
    audio_thread = threading.Thread(target=video_clip.audio.preview)
    audio_thread.start()
    
    cap = cv2.VideoCapture(video_path)

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

    cap.release()
    audio_thread.join()

if __name__ == "__main__":
    video_path = "/home/bob/Downloads/cartoon.mp4"  # Replace with your video file path
    play_video_with_audio(video_path)
