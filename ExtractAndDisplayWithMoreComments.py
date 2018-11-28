#!/usr/bin/env python3

# AM: All I'm doing here is rearranging the comments and adding my own comments in an effort to better understand the code
import threading
import cv2				#cv stands for Computer Vision
import numpy as np
import base64
import queue

"""input is the FileName of the Clip and the name of the Queue the the extracted Frames are put into.
"basically the return type is void" the method modifies the outputBuffer and gives some print Lines."""
def extractFrames(fileName, outputBuffer):     
    count = 0								# Initialize frame count    
    vidcap = cv2.VideoCapture(fileName)		# open video file    
    success,image = vidcap.read()			# read first image    
    print("Reading frame {} {} ".format(count, success))
    
    """ according to the pytho3 help() for cv2.VideoCapture the read() :
    read([, image]) -> retval, image		Meaning that .read() returns a boolean and an image
    "If no frames has (sic) been grabbed (camera disconnected, or there are no more 
    frames in the video file), the method returns false and the function returns empty image" """
    while success:
        success, jpgImage = cv2.imencode('.jpg', image)		# get a jpg encoded frame
        jpgAsText = base64.b64encode(jpgImage)				# encode the frame as base 64 to make debugging easier			#This is for better debugging
        outputBuffer.put(jpgAsText)							# add the frame to the buffer
       
        success,image = vidcap.read()
        print('Reading frame {} {}'.format(count, success))
        count += 1
    print("Frame extraction complete")

"""This method takes the same Buffer, that is modified by the other method, as input.
"basically the return type is also void" the method opens a Window and displays each frame for 42ms. """
def displayFrames(inputBuffer):    
    count = 0					# initialize frame count

    # go through each frame in the buffer until the buffer is empty
    while not inputBuffer.empty():        
        frameAsText = inputBuffer.get()									# get the next frame
        jpgRawImage = base64.b64decode(frameAsText)						# decode the frame
        jpgImage = np.asarray(bytearray(jpgRawImage), dtype=np.uint8)	# convert the raw frame to a numpy array
        img = cv2.imdecode( jpgImage ,cv2.IMREAD_UNCHANGED)				# get a jpg encoded frame
        print("Displaying frame {}".format(count))        

        # display the image in a window called "video" and wait 42ms before displaying the next frame
        cv2.imshow("Video", img)
        if cv2.waitKey(42) and 0xFF == ord("q"):
            break
        count += 1

    print("Finished displaying all frames")    
    cv2.destroyAllWindows()		# cleanup the windows

filename = 'clip.mp4'						# filename of clip to load
extractionQueue = queue.Queue()				# shared queue
extractFrames(filename,extractionQueue)		# extract the frames
displayFrames(extractionQueue)				# display the frames
