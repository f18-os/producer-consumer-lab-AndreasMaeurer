# taken mostly from https://www.bogotobogo.com/python/Multithread/python_multithreading_Synchronization_Producer_Consumer_using_queue.php
#I changed the Queue to queue. So basically I changed it from python2 to python3

"""
From one of Dr. Freudenthal's emails:

consider building the following simpler pipeline using producer-consumer coordination:

	* a "producer" of integers 1...20
	* a "processor" of integers that adds 1000 to each value
	* a consumer who prints integers

... and don't stop working this problem until you figure out how to have the processor & consumer shut down cleanly when the producer of integers is done.
(perhaps produce a None after the last integer, and deal with it all the way downsream)
"""
"""
So, breaking it into an even smaller piece first:
	* a "producer" of integers 1...20
	* a consumer who prints integers
"""

import threading
from threading import Thread
import time
import logging
import random
import queue as queue			#Python3

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s',)

# shared queue
BUF_SIZE = 10
q = queue.Queue(BUF_SIZE)

#semaphores
sem_putExt = threading.Semaphore(10)	#put Extraction
sem_getExt = threading.Semaphore(0)		#get Extraction

def producr():
	index = 0
	while (index < 20):		
		#print("reached")		#for debugging
		if not q.full():
			item = index+1 
			sem_putExt.acquire()
			q.put(item)			
			logging.debug('Putting ' + str(item) + ' : ' + str(q.qsize()) + ' items in queue')
			time.sleep(random.random())  #for fun
			index += 1
			sem_getExt.release()
	return
	
def consumr():
	while  not q.empty():
		sem_getExt.acquire()
		item = q.get()						
		logging.debug('*Getting* ' + str(item) + ' : ' + str(q.qsize()) + ' items in queue')
		time.sleep(random.random())
		sem_putExt.release()
	return

if __name__ == '__main__':
	thread1 = Thread(target = producr, args=[])
	thread2 = Thread(target = consumr, args=[])
	thread1.start()
	thread2.start()
