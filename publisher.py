from redisSubPub import RedisSubPub

def main():
    rsp = RedisSubPub()
    channel_name = raw_input("Enter channel name to which you want to publish messages: ")

    var = 1
    while var == 1:
        new_message = raw_input("Enter message you want to publish: ")
        rsp.publish(channel_name, new_message)


if __name__ == "__main__":
    main()
