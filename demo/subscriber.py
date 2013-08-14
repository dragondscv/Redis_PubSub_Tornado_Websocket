#!/home/y/bin/python2.6
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '../lib'))
from redisPubSub import RedisPubSub
import threading


rsp = RedisPubSub()

def sub_listener(channel_name):
    print("subscribe to "+channel_name)
    rsp.psubscribe(channel_name)

    #print "there are active channels:"
    #print rsp.count_active_channels("*")

    for message in rsp.listen():
      print message



def main():
    channel_name = raw_input("Enter channel name you want to subscribe: ")

    redisThread = threading.Thread(target=sub_listener(channel_name))
    redisThread.daemon = True
    redisThread.start()


if __name__ == "__main__":
    main()
