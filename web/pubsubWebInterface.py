#!/home/y/bin/python2.6

import collections
import types
import logging
import redis
import threading
import os.path
import sys
import json
import uuid
import weakref
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.websocket
import tornado.web
from tornado.escape import json_encode
from tornado.options import define, options
from functools import partial

# import redis python pubsub library
sys.path.append(os.path.join(os.path.dirname(__file__), '../lib'))
from redisPubSub import RedisPubSub


define("webserver_port", default=8888, help="Web server port", type=int)
define("redis_hostname", default="localhost", help="Redis host address")
define("redis_port", default=6379, help="Redis host port")

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

response_format = ['json', 'html']
response_format_string = '('+'|'.join(response_format)+')'



class RedisPubSubThread(threading.Thread):
    """
    subscribes to a redis pubsub channel and routes
    messages to subscribers

    messages have this format
    {'channel': ..., 'data': ...}
    """

    def __init__(self, redis_hostname, redis_port, redis_password=None):
        threading.Thread.__init__(self)

        self.pubsub = RedisPubSub(
            redis_hostname,
            redis_port
        )
        self.subscriptions = collections.defaultdict()

        # subscribe to dummy channel to make the thread alive
        self.pubsub.subscribe("dummy")
        print self.pubsub

    def subscribe(self, channel, callback):
        print "%s subscribe %s" %(self.pubsub, channel)
        self.pubsub.psubscribe(channel)
        self.subscriptions[channel] = callback

    def unsubscribe(self, channel):
        print "%s unsubscribe %s" %(self.pubsub, channel)
        self.pubsub.punsubscribe(channel)
        del self.subscriptions[channel]

    def disconnect(self):
        self.pubsub.unsubscribe("dummy")
        self.pubsub.disconnect()

    def notify(self, channel, data):
        print "notify callback..."
        #while True:
        print self.subscriptions
        try:
            cb = self.subscriptions[channel]
        except IndexError:
            #break
            pass

        if isinstance(cb, (weakref.ref,)):
            cb = cb()
        if cb is not None:
            cb(data, channel)

    def run(self):
        try:
            for message in self.pubsub.listen():
                print message
                if message['type'] == 'message' or message['type'] == 'pmessage':
                    self.notify(message['channel'], message['data'])
        except Exception as e:
            print e


class MainHandler(tornado.web.RequestHandler):
    def post(self):
        pass

    def get(self, *args):
        rsp = RedisPubSub()
        field = "build_time_in_millis"

        if (len(args) == 2 and args[0]):
            field = args[0]
            reverse = args[1] == "True"
            builds = rsp.get_all_sorted(field, reverse)
            html = self.render_string("all_events_sorted.html", builds=builds)
            self.write(html)
        else:
            hosts = rsp.get_all_hosts()
            builds = rsp.get_all_sorted(field, True)
            self.render("home.html", hosts=hosts, builds=builds)

        rsp.disconnect()

class SubscribeHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("subscribe.html", messages=[]);


"""
  Web service of sorting.
  Return json.
"""
class FilterHandler(tornado.web.RequestHandler):
    def get(self, filter_field, value, format=json):
        self.rsp = RedisPubSub()

        if (filter_field == "age"):
          builds = self.get_all_filtered_by_age(value)
        elif (filter_field == "host"):
          builds = self.get_all_filtered_by_host(value)
        elif (filter_field == "status"):
          builds = self.get_all_filtered_by_status(value)

        if (format == "json"):
            self.write(json_encode(builds))
        elif (format == "html"):
            self.render("all_events_sorted.html", builds=builds)

        self.rsp.disconnect()

    def get_all_filtered_by_age(self, age):
        reverse = True
        return self.rsp.get_all_filtered_by_age(int(age), reverse)

    def get_all_filtered_by_host(self, host):
        reverse = True
        return self.rsp.get_all_filtered_by_host(host, reverse)

    def get_all_filtered_by_status(self, status, format=json):
        # get all builds
        count = sys.maxint
        method_to_call = "list_"+status+"_builds"

        buildnames = getattr(self.rsp, method_to_call)(count)
        builds = []

        for buildname in buildnames:
            build = self.rsp.get_build(buildname[0])
            builds.append(build)

        return builds

class SortHandler(tornado.web.RequestHandler):
    def get(self, sort_field, count, format=json):
        method_to_call = "list_builds_by_"+sort_field

        rsp = RedisPubSub()
        builds = getattr(rsp, method_to_call)(count)

        if (format == "json"):
            self.write(json_encode(builds))
        elif (format == "html"):
            self.render("sort.html", count=count, sort_field=sort_field, limit=count, builds=builds)

        rsp.disconnect()

class GetByStatusHandler(tornado.web.RequestHandler):
    def get(self, status, count, format=json):
        method_to_call = "list_"+status+"_builds"

        rsp = RedisPubSub()
        builds = getattr(rsp, method_to_call)(count)

        if (format == "json"):
            self.write(json_encode(builds))
        elif (format == "html"):
            self.render("status.html", count=count, status=status, limit=count, builds=builds)

        rsp.disconnect()

class QueryHandler(tornado.web.RequestHandler):
    def get(self, *args):
        type = args[0]
        format = args[1]
        method_to_call = "get_all_"+type

        rsp = RedisPubSub()
        data = getattr(rsp, method_to_call)()
        if (format == "json"):
            self.write(json_encode(list(data)))
        elif (format == "html"):
            self.write("HTML format not support.")

        rsp.disconnect()

class GetHandler(tornado.web.RequestHandler):
    def get(self, *args):
        rsp = RedisPubSub()
        length = len(args)
        host = args[0]
        format = args[length-1]
        data = []

        if (length == 2):
            data = rsp.get_jobs(host)
        elif (length == 3):
            job = args[1]
            data = rsp.get_builds(host, job)
        elif (length == 4):
            job = args[1]
            build = args[2]
            data = rsp.get_build(host, job, build)

        if (format == "json"):
            self.write(json_encode(data))
        elif (format == "html"):
            self.write("HTML format not support.")

        rsp.disconnect()

"""
  Websocket handler.
"""
class RealtimeHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        # the id of the web socket
        self.id = uuid.uuid4()
        print"Open websocket %i" %(self.id)

        #subscriptions[self.id] = {'id':self.id}
        self.pubsubThread = RedisPubSubThread(
            redis_hostname = options.redis_hostname,
            redis_port     = options.redis_port
        )
        self.pubsubThread.daemon = True
        self.pubsubThread.start()

    def on_message(self, *args):
        message = args[0]
        print "Websocket %i got message %r" %(self.id, message)
        print self.pubsubThread
        json_ = json.loads(message)
        print json_

        if ('func' in json_):
            if (json_['func'] == 'subscribe'):
                self.pubsubThread.subscribe(json_['channelName'], self.on_message)
            elif (json_['func'] == 'unsubscribe'):
                self.pubsubThread.unsubscribe(json_['channelName'])

        else:
            json_['channel_name'] = args[1]
            html = self.render_string("message.html", build=json_)
            self.write_message(html)


    def on_close(self):
        print "close web socket %i" %(self.id)
        print "close redis pubsub thread %s" %(self.pubsubThread)
        self.pubsubThread.disconnect()


def main():
    print("start server...");

    tornado.options.parse_command_line()
    application = tornado.web.Application([
        (r'/realtime', RealtimeHandler),
        (r'/subscribe', SubscribeHandler),
        (r'/filter/(age)/([0-9]+)/'+response_format_string, FilterHandler),
        (r'/filter/(host)/(.*)/'+response_format_string, FilterHandler),
        (r'/filter/(status)/(.*)/'+response_format_string, FilterHandler),
        (r'/sort/(.*)/([0-9]+)/'+response_format_string, SortHandler),
        (r'/build/(.*)/([0-9]+)/'+response_format_string, GetByStatusHandler),
        (r'/(hosts|jobs|builds)/'+response_format_string, QueryHandler),
        (r'/(.*)/(.*)/([0-9]+)/'+response_format_string, GetHandler),
        (r'/(.*)/(.*)/'+response_format_string, GetHandler),
        (r'/(.*)/'+response_format_string, GetHandler),
        (r'/(.*)/(True|False)', MainHandler),
        (r'/', MainHandler)
    ], **settings)


    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.webserver_port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
