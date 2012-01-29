#!/usr/bin/env python2
#
# OpenCV Python reference: http://opencv.willowgarage.com/documentation/python/index.html

import cv
import Key
import random

class Target:
    """ Class representing the target """
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 0
        self.height = 0
        self.speed = (0,1)
        self.active = True

    def getDimensions(self):
        return (self.x, self.y, self.width, self.height)

    def centerOrigin(self):
        return (self.x - self.width/2, self.y - self.height/2)

    def update(self):
        self.x += self.speed[0]
        self.y += self.speed[1]

# Create windows to show the captured images
cv.NamedWindow("window_a", cv.CV_WINDOW_AUTOSIZE)
cv.NamedWindow("window_b", cv.CV_WINDOW_AUTOSIZE)

# Structuring element
es = cv.CreateStructuringElementEx(9,9, 4,4, cv.CV_SHAPE_ELLIPSE)

## Webcam settings
# Use default webcam.
# If that does not work, try 0 as function's argument
cam = cv.CaptureFromCAM(-1)
# Dimensions of player's webcam
frame_size = (int(cv.GetCaptureProperty(cam, cv.CV_CAP_PROP_FRAME_WIDTH)),int(cv.GetCaptureProperty(cam, cv.CV_CAP_PROP_FRAME_HEIGHT)))

## Video settings
# Set to True if you want to record a video of the game
writeVideo = False
# Video format
fourcc = cv.FOURCC('M', 'J', 'P', 'G')
fps = 30
# Create video file
if writeVideo:
    video_writer = cv.CreateVideoWriter("movie.avi", fourcc, fps, frame_size)

previous = cv.CreateImage(frame_size, 8L, 3)
cv.SetZero(previous)

difference = cv.CreateImage(frame_size, 8L, 3)
cv.SetZero(difference)

current = cv.CreateImage(frame_size, 8L, 3)
cv.SetZero(current)

bola_original = cv.LoadImage("Aqua-Ball-Red-icon.png")
bola = cv.CreateImage((64,64), bola_original.depth, bola_original.channels)
cv.Resize(bola_original, bola)

mask_original = cv.LoadImage("input-mask.png")
mask = cv.CreateImage((64,64), mask_original.depth, bola_original.channels)
cv.Resize(mask_original, mask)

def hit_value(image, target):
    roi = cv.GetSubRect(image, target.getDimensions())
    return cv.CountNonZero(roi)

def create_targets(count):
    targets = list()
    for i in range(count):
        tgt = Target(random.randint(0, frame_size[0]-bola.width), 0)
        tgt.width = bola.width
        tgt.height = bola.height
        targets.append(tgt)

    return targets

nbolas = 5
targets = create_targets(nbolas)

initialDelay = 100

score = 0

font = cv.InitFont(cv.CV_FONT_HERSHEY_SIMPLEX, 1, 1)

# capture - original footage
# current - blurred footage
# difference - difference frame
# frame - difference frame gray scaled > threshold > dilate | working image
# bola_original - imagem da bola
# bola - imagem da bola menor
# mask_original - imagem da mascara
# mask - imagem da mascara menor
# Main loop
while True:
    # Capture a frame
    capture = cv.QueryFrame(cam)
    cv.Flip(capture, capture, flipMode=1)

    # Difference between frames
    cv.Smooth(capture, current, cv.CV_BLUR, 15,15)
    cv.AbsDiff(current, previous, difference)

    frame = cv.CreateImage(frame_size, 8, 1)
    cv.CvtColor(difference, frame, cv.CV_BGR2GRAY)
    cv.Threshold(frame, frame, 10, 0xff, cv.CV_THRESH_BINARY)
    cv.Dilate(frame, frame, element=es, iterations=3)

    if initialDelay <= 0:
        for t in targets:
            if t.active:
                nzero = hit_value(frame, t)
                if nzero < 1000:
                    # Draws the target to screen
                    cv.SetImageROI(capture, t.getDimensions())
                    cv.Copy(bola, capture, mask)
                    cv.ResetImageROI(capture)
                    t.update()
                    # If the target hits the bottom
                    if t.y + t.height >= frame_size[1]:
                        t.active = False
                        nbolas -= 1
                else:
                    t.y = 0
                    t.x = random.randint(0, frame_size[0]-bola.width)
                    if t.speed[1] < 15:
                        t.speed = (0, t.speed[1]+1)
                    score += nbolas

    cv.PutText(capture, "Score: %d" % score, (10,frame_size[1]-10), font, cv.RGB(0,0,0))
    cv.ShowImage("window_a", frame)
    if writeVideo:
        cv.WriteFrame(video_writer, capture)
    cv.ShowImage("window_b", capture)

    previous = cv.CloneImage(current)

    # Exit game if ESC key is pressed
    c = Key.WaitKey(2)
    if c == 27:
        break

    initialDelay -= 1

print score
