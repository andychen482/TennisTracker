# TennisTracker

![](https://github.com/andychen482/TennisTracker/blob/main/gif/jacksock_cut_traj-ezgif.com-video-to-gif-converter.gif)

Currently models in development.

## TrackNetV2 for tennis court
Detect corners on close side, perform homography to find all tennis court points.
Calculate transformation matrix.

## TrackNetV2 for tennis ball tracking
3 frame tensors to provide context
Detect position of ball

## TimeSeriesForestClassifier
Detect bounces

Find coordinates of bounce locations, perform perspective transforms to find location of bounces on tennis court, similar to SwingVision.
