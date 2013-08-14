#!/home/y/bin/python2.6

from functools import partial
import types
import logging
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.websocket
import tornado.web
import redis
import threading
import os.path
import json
import uuid

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '../lib'))
from redisPubSub import RedisPubSub

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)

settings = dict(
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=False,
            debug=True,
        )
#{
#  'auto_reload': True,
#}


LISTENERS = []

rsp = RedisPubSub()


def sub_listener():

    # subscribe to some test channel to keep this thread running
    # do not remove this line
    channel_name = "test"
    rsp.subscribe(channel_name)

    io_loop = tornado.ioloop.IOLoop.instance()
    for message in rsp.listen():
        print("get a message.")
        print LISTENERS
        for element in LISTENERS:
            print("send to listeners.")
            io_loop.add_callback(partial(element.on_message, message))


class MainHandler(tornado.web.RequestHandler):

    def subscribe(self, channel_name):
        print("subscribe channel "+channel_name)
        print LISTENERS

        rsp.psubscribe(channel_name)
        rsp.publish(channel_name, "test");

        for t in threading.enumerate():
            print t

    def unsubscribe(self, channel_name):
        print("unsubscribe channel "+channel_name)
        rsp.punsubscribe(channel_name)

    def post(self):
        channel_name = self.get_argument("channelName")
        func = self.get_argument("func")

        if (func == "sub"):
            self.subscribe(channel_name)
            results = {"status": "success", "channelName": channel_name}
            json_ = tornado.escape.json_encode(results)
            self.write(json_)

        elif (func == "unsub"):
            self.unsubscribe(channel_name)
            results = {"status": "success"}
            json_ = tornado.escape.json_encode(results)
            self.write(json_)

    def get(self):

        print("start thread...");
        redisThread = threading.Thread(target=sub_listener)
        redisThread.daemon = True
        redisThread.start()
        print redisThread
        print redisThread.isAlive()


        slaves = rsp.get_all()
        #print(slaves)

        limit = 50
        sortByDuration = rsp.list_builds_by_duration(limit)
        sortByTime = rsp.list_builds_by_time(limit)
        sortByStartTime = rsp.list_builds_by_start_time(limit)
        count_successful = rsp.count_successful_builds()
        successful_builds = rsp.list_successful_builds(limit)
        count_failed = rsp.count_failed_builds()
        failed_builds = rsp.list_failed_builds(limit)
        count_aborted = rsp.count_aborted_builds()
        aborted_builds = rsp.list_aborted_builds(limit)
        count_not_built = rsp.count_not_built_builds()
        not_built_builds = rsp.list_not_built_builds(limit)
        count_unstable = rsp.count_unstable_builds()
        unstable_builds = rsp.list_unstable_builds(limit)

        self.render("index.html", slaves=slaves, limit=limit,
            sortByDuration=sortByDuration,
            sortByTime=sortByTime,
            sortByStartTime=sortByStartTime,
            count_successful=count_successful, successful_builds=successful_builds,
            count_failed=count_failed, failed_builds=failed_builds,
            count_aborted=count_aborted, aborted_builds=aborted_builds,
            count_not_built=count_not_built, not_built_builds=not_built_builds,
            count_unstable=count_unstable, unstable_builds=unstable_builds,
            messages=[])


        print "%d unstable builds sorted by start time:"%limit
        for build, duration in sortByStartTime:
          print build, duration


class RealtimeHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        self.id = uuid.uuid4()
        print("open websocket and add listener...")
        LISTENERS.append(self)
        print LISTENERS

    def on_message(self, message):
        print("got message %r", message)
        if (type(message['data']) != types.LongType ):
          channel_name = message['channel']
          json_ = json.loads(message['data'])
          json_['channel_name'] = channel_name
          html = self.render_string("message.html", data=json_)
          self.write_message(html)

    def on_close(self):
        print("close listeners...")
        LISTENERS.remove(self)
        print LISTENERS


def main():
    print("start server...");

    tornado.options.parse_command_line()
    application = tornado.web.Application([
        (r"/", MainHandler),
        (r'/realtime', RealtimeHandler),
        (r'/subscribe', MainHandler),
        (r'/unsubscribe', MainHandler),
    ], **settings)


    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()