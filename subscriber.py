from redisSubPub import RedisSubPub
import threading


rsp = RedisSubPub()

def sub_listener(channel_name):
    print("subscribe to "+channel_name)
    rsp.psubscribe(channel_name)
    
    for message in rsp.listen():
      print message

def main():


    channel_name = raw_input("Enter channel name you want to subscribe: ")

    redisThread = threading.Thread(target=sub_listener(channel_name))
    redisThread.daemon = True
    redisThread.start()


if __name__ == "__main__":
    main()
