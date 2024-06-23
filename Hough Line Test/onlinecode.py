'''
Code to take an image of a court, run houghline transforms,
merge overlapping lines, and display the result
'''

import math
import numpy as np
import cv2
import os

class HoughBundler:     
    def __init__(self,min_distance=5,min_angle=2):
        self.min_distance = min_distance
        self.min_angle = min_angle
    
    def get_orientation(self, line):
        orientation = math.atan2(abs((line[3] - line[1])), abs((line[2] - line[0])))
        return math.degrees(orientation)

    def check_is_line_different(self, line_1, groups, min_distance_to_merge, min_angle_to_merge):
        for group in groups:
            for line_2 in group:
                if self.get_distance(line_2, line_1) < min_distance_to_merge:
                    orientation_1 = self.get_orientation(line_1)
                    orientation_2 = self.get_orientation(line_2)
                    if abs(orientation_1 - orientation_2) < min_angle_to_merge:
                        group.append(line_1)
                        return False
        return True

    def distance_point_to_line(self, point, line):
        px, py = point
        x1, y1, x2, y2 = line

        def line_magnitude(x1, y1, x2, y2):
            line_magnitude = math.sqrt(math.pow((x2 - x1), 2) + math.pow((y2 - y1), 2))
            return line_magnitude

        lmag = line_magnitude(x1, y1, x2, y2)
        if lmag < 0.00000001:
            distance_point_to_line = 9999
            return distance_point_to_line

        u1 = (((px - x1) * (x2 - x1)) + ((py - y1) * (y2 - y1)))
        u = u1 / (lmag * lmag)

        if (u < 0.00001) or (u > 1):
            #// closest point does not fall within the line segment, take the shorter distance
            #// to an endpoint
            ix = line_magnitude(px, py, x1, y1)
            iy = line_magnitude(px, py, x2, y2)
            if ix > iy:
                distance_point_to_line = iy
            else:
                distance_point_to_line = ix
        else:
            # Intersecting point is on the line, use the formula
            ix = x1 + u * (x2 - x1)
            iy = y1 + u * (y2 - y1)
            distance_point_to_line = line_magnitude(px, py, ix, iy)

        return distance_point_to_line

    def get_distance(self, a_line, b_line):
        dist1 = self.distance_point_to_line(a_line[:2], b_line)
        dist2 = self.distance_point_to_line(a_line[2:], b_line)
        dist3 = self.distance_point_to_line(b_line[:2], a_line)
        dist4 = self.distance_point_to_line(b_line[2:], a_line)

        return min(dist1, dist2, dist3, dist4)

    def merge_lines_into_groups(self, lines):
        groups = []  # all lines groups are here
        # first line will create new group every time
        groups.append([lines[0]])
        # if line is different from existing gropus, create a new group
        for line_new in lines[1:]:
            if self.check_is_line_different(line_new, groups, self.min_distance, self.min_angle):
                groups.append([line_new])

        return groups

    def merge_line_segments(self, lines):
        orientation = self.get_orientation(lines[0])
      
        if(len(lines) == 1):
            return np.block([[lines[0][:2], lines[0][2:]]])

        points = []
        for line in lines:
            points.append(line[:2])
            points.append(line[2:])
        if 45 < orientation <= 90:
            #sort by y
            points = sorted(points, key=lambda point: point[1])
        else:
            #sort by x
            points = sorted(points, key=lambda point: point[0])

        return np.block([[points[0],points[-1]]])

    def process_lines(self, lines):
        lines_horizontal  = []
        lines_vertical  = []
  
        for line_i in [l[0] for l in lines]:
            orientation = self.get_orientation(line_i)
            # if vertical
            if 45 < orientation <= 90:
                lines_vertical.append(line_i)
            else:
                lines_horizontal.append(line_i)

        lines_vertical  = sorted(lines_vertical , key=lambda line: line[1])
        lines_horizontal  = sorted(lines_horizontal , key=lambda line: line[0])
        merged_lines_all = []

        # for each cluster in vertical and horizantal lines leave only one line
        for i in [lines_horizontal, lines_vertical]:
            if len(i) > 0:
                groups = self.merge_lines_into_groups(i)
                merged_lines = []
                for group in groups:
                    merged_lines.append(self.merge_line_segments(group))
                merged_lines_all.extend(merged_lines)
                    
        return np.asarray(merged_lines_all)
    
def line_intersection(line1, line2):
    # Extract points for readability
    x1, y1, x2, y2 = line1[0]
    x3, y3, x4, y4 = line2[0]

    # Function to calculate the determinant of a 2x2 matrix
    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    # Calculate differences in x and y coordinates
    xdiff = (x1 - x2, x3 - x4)
    ydiff = (y1 - y2, y3 - y4)

    # Calculate determinant to check if lines are parallel
    div = det(xdiff, ydiff)
    if div == 0:
        return None  # Lines are parallel

    # Calculate determinants for the coordinates
    d1 = det((x1, y1), (x2, y2))
    d2 = det((x3, y3), (x4, y4))

    # Calculate the x and y coordinates of the intersection point
    x = det((d1, d2), xdiff) / div
    y = det((d1, d2), ydiff) / div

    # Check if the intersection point is within both line segments
    if min(x1 - 10, x2 - 10) <= x <= max(x1 + 10, x2 + 10) and min(y1 - 10, y2 - 10) <= y <= max(y1 + 10, y2 + 10) and \
       min(x3 - 10, x4 - 10) <= x <= max(x3 + 10, x4 + 10) and min(y3 - 10, y4 - 10) <= y <= max(y3 + 10, y4 + 10):
        return [x, y]

    return None  # Intersection point not within the bounds of both segments

if __name__ == "__main__":
    folder_path = 'court_training'
    files = [file for file in os.listdir(folder_path) if file.endswith('.png') or file.endswith('.jpg')]
    files.sort()  # Ensure the files are sorted if needed
    current_index = 0

    cv2.namedWindow("img", cv2.WINDOW_NORMAL)

    while True:
        file_path = os.path.join(folder_path, files[current_index])
        print(f"Processing {file_path}")
        img = cv2.imread(file_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, thresh1 = cv2.threshold(gray, 190, 255, cv2.THRESH_BINARY)
        lines = cv2.HoughLinesP(thresh1, 1, np.pi / 180, 30, None, 300, 100)
        
        bundler = HoughBundler(min_distance=10, min_angle=5)
        if lines is not None:
            lines = bundler.process_lines(lines)
            for line in lines:
                cv2.line(img, (line[0][0], line[0][1]), (line[0][2], line[0][3]), (0, 255, 0), 2)

            for line1 in lines:
                for line2 in lines:
                    intersect = line_intersection(line1, line2)
                    if intersect is not None:
                        cv2.circle(img, (int(intersect[0]), int(intersect[1])), 1, (0, 0, 255), 5)

        cv2.imshow("img", img)
        
        key = cv2.waitKey(0)
        if key == 27:  # ESC key to exit
            break
        elif key == 97:  # Left arrow key
            current_index = max(0, current_index - 1)
        elif key == 100:  # Right arrow key
            current_index = min(len(files) - 1, current_index + 1)

    cv2.destroyAllWindows()