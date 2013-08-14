#!/home/y/bin/python2.6
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '../lib'))
from redisPubSub import RedisPubSub

def main():
    rsp = RedisPubSub()
    channel_name = raw_input("Enter channel name to which you want to publish messages: ")

    var = 1
    while var == 1:
        new_message = raw_input("Enter message you want to publish: ")
        rsp.publish(channel_name, new_message)


if __name__ == "__main__":
    main()
