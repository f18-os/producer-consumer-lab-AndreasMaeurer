# some code taken from: https://www.bogotobogo.com/python/Multithread/python_multithreading_Synchronization_Producer_Consumer_using_queue.php
"""
Producer Consumer Lab
OS Fall 2018
"""

import threading
from threading import Thread
import time
import logging
import random
import queue as queue			#Python3
import cv2
import base64
import numpy as np

BUF_SIZE = 10
# shared Queue
colorQueue = queue.Queue(BUF_SIZE)
# output Queue
grayQueue = queue.Queue(BUF_SIZE)

#semaphores
sem_putExt = threading.Semaphore(10)	#put Extraction
sem_getExt = threading.Semaphore(0)		#get Extraction
sem_putOut = threading.Semaphore(10)	#put Output
sem_getOut = threading.Semaphore(0)		#get Output

#The first producer extracts the frames from the video
"""input is the FileName of the Clip and the name of the Queue the the extracted Frames are put into.
"basically the return type is void" the method modifies the grayQueue and gives some print Lines."""
#The "extractFrames" method slightly modified:
def producr(fileName):     
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
        
        sem_putExt.acquire()
        colorQueue.put(jpgAsText)							# add the frame to the buffer
        sem_getExt.release()        
        
        success,image = vidcap.read()
        print('Reading frame {} {}'.format(count, success))
        count += 1
    print("Frame extraction complete")
    
    sem_putExt.acquire()
    extractionQueue.put("Frame extraction complete")
    sem_getExt.release()

#first consumer and second producer in one (so processor...)
#convertToGreyscale:
def processr():    
    while True:
        sem_getExt.acquire()
        frameAsText = colorQueue.get()
        
        if(frameAsText == "Frame extraction complete"):
            #sem_putOut.acquire()
            grayQueue.put("Break")
            print("Gray Done")
            sem_getOut.release()
            break        
        sem_putExt.release()
        
        #from ExtractAndDisplay      
        jpgRawImage = base64.b64decode(frameAsText)						#decode the frame
        jpgImage = np.asarray(bytearray(jpgRawImage), dtype=np.uint8)	# convert the raw frame to a numpy array
        img = cv2.imdecode( jpgImage ,cv2.IMREAD_UNCHANGED)				# get a jpg encoded frame
        
        #from ConvertToGrayscale
        grayscaleFrame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)			# convert the image to grayscale
        success, jpgImage = cv2.imencode('.jpg', grayscaleFrame)		# get a jpg encoded frame
        
        #from ExtractFrames  
        jpgAsText = base64.b64encode(jpgImage)		#encode the frame as base 64 to make debugging easier
        
        #convert to grayscale
        sem_putOut.acquire()
        grayQueue.put(jpgAsText)
        sem_getOut.release()
  
"""This method takes the  Buffer, that is modified by the other method, as input.
"basically the return type is also void" the method opens a Window and displays each frame for 42ms. """
#displayFrames method from ExtractAndDisplay.py  comments rearranged to make it easier to read
def consumr():
    # initialize frame count
    count = 0

    # go through each frame in the buffer until the buffer is empty
    while True:
        # get the next frame
        sem_getOut.acquire()
        frameAsText = grayQueue.get()
        
        if(frameAsText == "Break"):
           print("finished")
           break
        
        sem_putOut.release()
       
        jpgRawImage = base64.b64decode(frameAsText)						# decode the frame
        jpgImage = np.asarray(bytearray(jpgRawImage), dtype=np.uint8)	# convert the raw frame to a numpy array
        img = cv2.imdecode( jpgImage ,cv2.IMREAD_UNCHANGED)				# get a jpg encoded frame

        print("Displaying frame {}".format(count))        

        # display the image in a window called "video" and wait 42ms
        # before displaying the next frame
        cv2.imshow("Video", img)
        if cv2.waitKey(42) and 0xFF == ord("q"):
            break

        count += 1

    print("Finished displaying all frames")
    # cleanup the windows
    cv2.destroyAllWindows()

if __name__ == '__main__':
	thread1 = Thread(target = producr, args=['clip.mp4'])
	thread2 = Thread(target = processr, args=[])
	thread3 = Thread(target = consumr, args=[])	
	thread1.start()
	thread2.start()
	thread3.start()
