'''
Created on Dec 9, 2010

@author: gaubert
'''
import sys
import zmq

import json
import threading
import time



def main():
    
    #zmrl = 'tcp://127.0.0.1:6005'
    zmrl = "tcp://*:5560"
    i = 0
    context = zmq.Context()
    
    socket = context.socket(zmq.XREQ)
    socket.setsockopt(zmq.IDENTITY,"w%d" % (i))
    
    socket.connect(zmrl)
    
    
    print("=W%d= Connected to %s socket.\n" %(i, zmrl))

    #send READY to server
    socket.send("READY")

    while True:
        #first frame is empty
        print("=W%d= Wait for some work to do.\n" % (i))
        message = socket.recv_multipart()
        print("=W%d= Got work to do. message = %s\n." % (i, message))
        time.sleep(1)
        print("=W%d= send process message back \n" %(i))
        message[-1] = "%s done" % (message[-1])
        socket.send_multipart(message)

if __name__ == "__main__":
    main()