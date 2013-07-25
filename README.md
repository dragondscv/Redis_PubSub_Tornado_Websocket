jenkins_plugin_eventnotification
================================

Files:
  test.py: the test code

  redisSubPub.py: the Redis API

  publisher.py: the publisher of pubsub example
  subscriber.py: the subscriber of pubsub example

  pubsubWebInterface.py: the web interface
  static: the javascript files for the web interface
  templates: the web page templates for web interface

Reqirements:
  Python 2.7
  Redis 2.6
  redis-py: the redis python client, https://github.com/andymccurdy/redis-py
  Tornado 3.1 (necessary for web interface)
