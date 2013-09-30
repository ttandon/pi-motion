#!/usr/bin/python

import cv
import sys
import csv

class Target:

    def __init__(self):
        if len(sys.argv) > 1: 
            self.capture = cv.CaptureFromFile(sys.argv[1])
            cv.NamedWindow("Target", 1)
        else:
            print "File does not exist"
            
        # open a file for saving point data
        self.outfile = open('./motion.txt', 'wb')
        self.csvwrite = csv.writer(self.outfile)

    def close(self):
        self.outfile.close()

    def run(self):
        coordinates = []
        ##analysis ranges
        XMIN = 72
        XMAX = 300
        YMIN = 99
        YMAX = 244
        ofile ="velocity.txt"
        filew = open(ofile, "w")
        # Capture first frame to get size
        frame = cv.QueryFrame(self.capture)
        frame_size = cv.GetSize(frame)
        width =  frame_size[0]
        height = frame_size[1]
        print width
        color_image = cv.CreateImage(cv.GetSize(frame), 8, 3)
        grey_image = cv.CreateImage(cv.GetSize(frame), cv.IPL_DEPTH_8U, 1)
        moving_average = cv.CreateImage(cv.GetSize(frame), cv.IPL_DEPTH_32F, 3)

        first = True

        while True:
            closest_to_left = cv.GetSize(frame)[0]
            closest_to_right = cv.GetSize(frame)[1]

            color_image = cv.QueryFrame(self.capture)
            if (color_image == None) :
                print "End of file reached"
                return

            # Smooth to get rid of false positives
            cv.Smooth(color_image, color_image, cv.CV_GAUSSIAN, 3, 0)

            if first:
                difference = cv.CloneImage(color_image)
                temp = cv.CloneImage(color_image)
                cv.ConvertScale(color_image, moving_average, 1.0, 0.0)
                first = False
            else:
                cv.RunningAvg(color_image, moving_average, 0.020, None)

            # Convert the scale of the moving average.
            cv.ConvertScale(moving_average, temp, 1.0, 0.0)

            # Minus the current frame from the moving average.
            cv.AbsDiff(color_image, temp, difference)

            # Convert the image to grayscale.
            cv.CvtColor(difference, grey_image, cv.CV_RGB2GRAY)

            # Convert the image to black and white.
            cv.Threshold(grey_image, grey_image, 70, 255, cv.CV_THRESH_BINARY)

            # Dilate and erode to get people blobs
            cv.Dilate(grey_image, grey_image, None, 18)
            cv.Erode(grey_image, grey_image, None, 10)

            storage = cv.CreateMemStorage(0)
            contour = cv.FindContours(grey_image, storage, cv.CV_RETR_CCOMP, cv.CV_CHAIN_APPROX_SIMPLE)
            print contour
            points = []
            while contour:
                bound_rect = cv.BoundingRect(list(contour))
                contour = contour.h_next()

                pt1 = (bound_rect[0], bound_rect[1])
                pt2 = (bound_rect[0] + bound_rect[2], bound_rect[1] + bound_rect[3])
                points.append(pt1)
                points.append(pt2)
                print points
                cv.Rectangle(color_image, pt1, pt2, cv.CV_RGB(255,0,0), 1)
                x_pos = abs(((bound_rect[0]+bound_rect[2])/2.0))
                y_pos = abs(((bound_rect[1]+bound_rect[3])/2.0)-height)-200
                if(x_pos>XMIN and x_pos<XMAX and y_pos>YMIN and y_pos<YMAX):
                    coordinates.append([x_pos, y_pos])
                    self.outfile.write(str(x_pos)+","+str(y_pos)+"\n")
            for i in xrange(1,len(coordinates)):
                x1 = coordinates[i][0]
                y1 = coordinates[i][1]
                x0 = coordinates[i-1][0]
                y0 = coordinates[i-1][1]
                if(x1!=x0 and x1>XMIN and x1<XMAX and y1>YMIN and y1<YMAX):
                    filew.write(str(x1)+","+str((y1-y0)/(x1-x0))+"\n")


            # if len(points):
            #     center_point = reduce(lambda a, b: ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), points)
            #     cv.Circle(color_image, center_point, 40, cv.CV_RGB(255, 255, 255), 1)
            #     cv.Circle(color_image, center_point, 30, cv.CV_RGB(255, 100, 0), 1)
            #     cv.Circle(color_image, center_point, 20, cv.CV_RGB(255, 255, 255), 1)
            #     cv.Circle(color_image, center_point, 10, cv.CV_RGB(255, 100, 0), 1)

            cv.ShowImage("Target", color_image)

            # Listen for ESC key

            c = cv.WaitKey(7) % 0x100
            if c == 27:
                break
            
if __name__=="__main__":
    t = Target()
    t.run()
    t.close()
