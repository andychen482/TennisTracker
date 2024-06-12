import cv2
import pandas as pd
import sys
import os

if len(sys.argv) != 2:
    print("Usage: python draw_on_video.py <video_file>")
    sys.exit(1)

video_file = sys.argv[1]
csv_file = f"{video_file.split('.')[0]}_ball.csv"

if not os.path.exists(csv_file):
    print(f"No CSV file found for {video_file}")
    sys.exit(1)

# Load the video
cap = cv2.VideoCapture(video_file)
if not cap.isOpened():
    print("Error: Could not open video.")
    sys.exit(1)

# Read the CSV file
df = pd.read_csv(csv_file)

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(f"{video_file.split('.')[0]}_annotated.mp4", fourcc, 30.0, (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))

while True:
    ret, frame = cap.read()
    if not ret:
        break

    current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES)) - 1
    if current_frame in df['Frame'].values:
        visibility = df[df['Frame'] == current_frame]['Visibility'].values[0]
        if visibility == 1:
            x = int(df[df['Frame'] == current_frame]['X'].values[0])
            y = int(df[df['Frame'] == current_frame]['Y'].values[0])
            cv2.circle(frame, (x, y), 10, (0, 0, 255), 2)

    out.write(frame)

cap.release()
out.release()
cv2.destroyAllWindows()

print("Video processing complete.")
