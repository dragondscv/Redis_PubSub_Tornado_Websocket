eventstream_redis_python_pubsub
===============================

Files:

  lib/redisPubSub.py: the Redis API. publisher.py, subscriber.py and pubsubWebInterface.py call it to talk to Redis

  test/
    test.py: the test code

  demo/
    publisher.py: the publisher of pubsub example
    subscriber.py: the subscriber of pubsub example

  web/
    pubsubWebInterface.py: the web interface
    static/
      pubsub.js: the javascript files for the web interface
    templates/: the web page templates for web interface
      base.html  home.html  message.html  sort.html  status.html  subscribe.html

Reqirements:
  Python 2.6

  Redis 2.6

  redis-py: the redis python client, https://github.com/andymccurdy/redis-py

  Tornado 2.2 (necessary for web interface)

Third party libraries used by this project:

  redis-py

Usage:
  1. $python2.6 demo/subscriber.py

    1.1 Enter channel name you want to subscribe: e.g., *

  2. $python2.6 demo/publisher.py

    2.1 Enter channel name to which you want to publish messages. e.g., test

    2.2 Enter message you want to publish. e.g., a test message

  3. You should receive the message from subscriber.

  4. Alternatively you can try to build a job on Jenkins master and run subscriber.py.
    You should receive event messages from subscriber by subscribing to correct job name
    (e.g., subscribing to '*' and you will receive everything).

  5. Run "$python2.6 web/pubsubWebInterface.py" to start Tornado web server.

    5.1 Go to "http://host_name:8888/" to use the web interface.
