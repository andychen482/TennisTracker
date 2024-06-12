import cv2
import numpy as np
import pandas as pd
import sys
import os

if len(sys.argv) != 2:
    print("Usage: python label_tool.py <video_file>")
    sys.exit(1)

video_file = sys.argv[1]
csv_file = f"{video_file.split('.')[0]}_ball.csv"

frame_data = []

if os.path.exists(csv_file):
    df = pd.read_csv(csv_file)
    frame_data = df.values.tolist()
    print("Resuming from saved data.")
else:
    print("Starting fresh labeling session.")

# Load the video
cap = cv2.VideoCapture(video_file)
if not cap.isOpened():
    print("Error: Could not open video.")
    sys.exit(1)

current_frame = frame_data[-1][0] if frame_data else 0
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

# Store original frames
original_frames = {}

# Set up mouse callback function
def click_event(event, x, y, flags, param):
    global frame, current_frame, original_frames
    if event == cv2.EVENT_LBUTTONDOWN:
        frame_data[current_frame] = [current_frame, 1, x, y]
        frame = original_frames[current_frame].copy()
        cv2.circle(frame, (x, y), 2, (0, 0, 255), 2)
        cv2.imshow('Video', frame)

cv2.namedWindow('Video')
cv2.setMouseCallback('Video', click_event)

while True:
    cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame.")
        break

    original_frames[current_frame] = frame.copy()

    if len(frame_data) <= current_frame:
        frame_data.extend([None] * (current_frame + 1 - len(frame_data)))

    if frame_data[current_frame] and frame_data[current_frame][1] == 1:
        _, _, x, y = frame_data[current_frame]
        cv2.circle(frame, (x, y), 2, (0, 0, 255), 2)

    print("Current frame:",current_frame)

    cv2.imshow('Video', frame)
    key = cv2.waitKey(0) & 0xFF

    if key == ord('q'):
        break
    elif key == ord('d'):
        if frame_data[current_frame] is None:
            frame_data[current_frame] = [current_frame, 0, 0, 0]
        if current_frame < total_frames - 1:
            current_frame += 1
    elif key == ord('e'):
        if current_frame > 0:
            current_frame -= 1
    elif key == ord('w'):
        frame_data[current_frame] = [current_frame, 0, 0, 0]
        frame = original_frames[current_frame].copy()
        cv2.imshow('Video', frame)
    elif key == ord('s'):
        if frame_data[current_frame] is None:
            frame_data[current_frame] = [current_frame, 0, 0, 0]
        # Save to CSV
        df = pd.DataFrame([d for d in frame_data if d is not None], columns=['Frame', 'Visibility', 'X', 'Y'])
        df.to_csv(f"{video_file.split('.')[0]}_ball.csv", index=False)
        print("Data saved.")

cap.release()
cv2.destroyAllWindows()
