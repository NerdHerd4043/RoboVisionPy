import cv2 as cv2
import argparse
import apriltag
import math

LINE_LENGTH = 5
CENTER_COLOR = (0, 255, 0)
CORNER_COLOR = (255, 0, 255)

### Some utility functions to simplify drawing on the camera feed
# draw a crosshair
def plot_point(image, center, color):
    center = (int(center[0]), int(center[1]))
    image = cv2.line(image,
                     (center[0] - LINE_LENGTH, center[1]),
                     (center[0] + LINE_LENGTH, center[1]),
                     color,
                     3)
    image = cv2.line(image,
                     (center[0], center[1] - LINE_LENGTH),
                     (center[0], center[1] + LINE_LENGTH),
                     color,
                     3)
    return image

# plot a little text
def plot_text(image, center, color, text):
    center = (int(center[0]) + 4, int(center[1]) - 4)
    return cv2.putText(image, str(text), center, cv2.FONT_HERSHEY_SIMPLEX,
                       1, color, 3)

def plot_center(image, center, color):
    center = (int(center[0]), int(center[1]))
    return cv2.putText(image, f"x:{center[0]}  y:{center[1]}  turn:{get_turn(center)}", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, color, 3)

def get_turn(center):
    x, _ = center
    # 1920 / 2 = 960 = center of screen/half of the screen
    return clamp_min_abs(-(960 - x) / 1920, 0.05)

def clamp_min_abs(value, min_abs):
    return value if abs(value) > min_abs else 0
  
def validate_corners(corners):
    c_0, c_1, c_2, c_3 = corners

    diff_x = c_0[0] - c_2[0]
    diff_y = c_0[1] - c_2[1]

    dist_sq = diff_x**2 + diff_y**2

    print(dist_sq)

    return not dist_sq < 5000


parser = argparse.ArgumentParser(description='Detect AprilTags from video stream.')
apriltag.add_arguments(parser)
options = parser.parse_args()

# setup and the main loop
detector = apriltag.Detector(options)
cam = cv2.VideoCapture(0)

looping = True

while looping:
    result, image = cam.read()
    grayimg = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

	# look for tags
    detections = detector.detect(grayimg)
    if not detections:
        print("Nothing")
    else:
        detected = False
	    # found some tags, report them and update the camera image
        for detect in detections:
            
            if validate_corners(detect.corners):
                detected = True
                print("tag_id: %s, center: %s" % (detect.tag_id, detect.center))
                image = plot_point(image, detect.center, CENTER_COLOR)
                image = plot_text(image, detect.center, CENTER_COLOR, detect.tag_id)
                image = plot_center(image, detect.center, CENTER_COLOR)
                for i, corner in enumerate(detect.corners):
                    image = plot_point(image, corner, CORNER_COLOR)
                    image = plot_text(image, corner, CORNER_COLOR, i)
            
        if not detected:
            print("Nothing")
	# refresh the camera image
    cv2.imshow('Result', image)
	# let the system event loop do its thing
    key = cv2.waitKey(100)
	# terminate the loop if the 'Return' key his hit
    if key == 13:
        looping = False

# loop over; clean up and dump the last updated frame for convenience of debugging
cv2.destroyAllWindows()
cv2.imwrite("final.png", image)
