#!/usr/bin/env python
#
# Copyright 2009 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

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
from redisSubPub import RedisSubPub

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

rsp = RedisSubPub()


def sub_listener():

    # subscribe to some test channel to keep this thread running
    # do not remove this line
    channel_name = "test"
    rsp.subscribe(channel_name)
    
    io_loop = tornado.ioloop.IOLoop.instance()
    for message in rsp.listen():
        print("get a message.")
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
        slaves = rsp.get_all()
        #print(slaves)
        self.render("index.html", slaves=slaves, messages=[])


class RealtimeHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print("open websocket and add listener...")
        LISTENERS.append(self)
 
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


def main():
    print("start server...");


    tornado.options.parse_command_line()
    application = tornado.web.Application([
        (r"/", MainHandler),
        (r'/realtime', RealtimeHandler),
        (r'/subscribe', MainHandler),
        (r'/unsubscribe', MainHandler),
    ], **settings)


    print("start thread...");
    redisThread = threading.Thread(target=sub_listener)
    redisThread.daemon = True
    redisThread.start()
    print redisThread
    print redisThread.isAlive()

    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
