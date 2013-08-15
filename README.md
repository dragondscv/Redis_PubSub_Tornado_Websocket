eventstream_redis_python_pubsub
===============================

Files:

  redisSubPub.py: the Redis API. publisher.py, subscriber.py and pubsubWebInterface.py call it to talk to Redis

  test/
    test.py: the test code

  demo/
      publisher.py: the publisher of pubsub example
      subscriber.py: the subscriber of pubsub example

  TODO: the pubsubWebInterface.py needs to be revised.
  pubsubWebInterface.py: the web interface
  static: the javascript files for the web interface
  templates: the web page templates for web interface

Reqirements:
  Python 2.7
  Redis 2.6
  redis-py: the redis python client, https://github.com/andymccurdy/redis-py
  Tornado 3.1 (necessary for web interface)

Usage:
  1. $python2.7 demo/subscriber.py
    1.1 Enter channel name you want to subscribe: e.g., *
  2. $python2.7 demo/publisher.py
    2.1 Enter channel name to which you want to publish messages. e.g., test
    2.2 Enter message you want to publish. e.g., a test message
  3. You should receive the message from subscriber.

  4. Alternatively you can try to build a job on Jenkins master and run subscriber.py. 
    You should receive event messages from subscriber by subscribing to correct job name 
    (e.g., subscribing to '*' and you will receive everything).
