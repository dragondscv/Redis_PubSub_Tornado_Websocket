import redis
import json

class RedisSubPub():

    def __init__(self, host='localhost', port=6379):
      self._rc = redis.StrictRedis(host, port, db=0)
      self._pubsub = self._rc.pubsub();

    "list all channels"
    def list_all_channels(self):
        return self.get_all_jobs()

    "get all hosts in the format of host_name"
    def get_all_hosts(self):
        return self._rc.smembers("hosts")

    "get all jobs in the format of host_name:job_name"
    def get_all_jobs(self):
        return self._rc.smembers("jobs")

    "get all builds in the format of host_name:job_name:build_name"
    def get_all_builds(self):
        return self._rc.smembers("builds")

    "return everything in database"
    def get_all(self):
        # get slaves
        slaves = self._rc.smembers("hosts")
        hashes = {}

        # get all jobs for each slave
        for slave in slaves:
            hashes[slave] = {}
            job_keys = self._rc.smembers(slave)

            for job_key in job_keys:
                job_name = job_key.split(':')[1]
                hashes[slave][job_name] = {}
                build_keys = self._rc.smembers(job_key)

                for build_key in build_keys:
                    build_no = build_key.split(':')[2]
                    hashes[slave][job_name][build_no] = self._rc.hgetall(build_key)

        return hashes

    "list builds sorted by duration"
    def list_builds_by_duration(self, limit, desc=True, withscores=True):
        return self._rc.zrange("sort:build_time_in_millis", 0, limit, desc, withscores)

    "list builds sorted by scheduled time"
    def list_builds_by_time(self, limit, desc=True, withscores=True):
        return self._rc.zrange("sort:build_time_in_millis", 0, limit, desc, withscores)

    "list builds sorted by start time"
    def list_builds_by_start_time(self, limit, desc=True, withscores=True):
        return self._rc.zrange("sort:build_start_time_in_millis", 0, limit, desc, withscores)

    "list successful builds"
    def list_successful_builds(self, limit):
        pass

    "list failed builds"
    def list_failed_builds(self, limit):
        pass


    def list_all_keys(self):
        hashes = self._rc.keys()
        return hashes



    def count_hosts(self):
        return self._rc.scard("hosts")

    def count_jobs(self):
        return self._rc.scard("jobs")

    def count_builds(self):
        return self._rc.scard("builds")

    def count_channels(self):
        return self._rc.scard("jobs")

    # not implemented yet because python client does not support this command
    def count_active_channels(self):
        pass


    def subscribe(self, channel_name):
        return self._pubsub.subscribe(channel_name)

    def psubscribe(self, channel_pattern):
        return self._pubsub.psubscribe(channel_pattern)

    def unsubscribe(self, channel_name):
        return self._pubsub.unsubscribe(channel_name)

    def punsubscribe(self, channel_pattern):
        return self._pubsub.punsubscribe(channel_pattern)

    def listen(self):
        return self._pubsub.listen()

    def publish(self, channel, message):
        return self._rc.publish(channel, message)

    """
      Return a pubsub instance that can be listened on.
      It should not be called unless you want to manually managing the subscription and
      publishing.
    """
    def pubsub(self):
        return self._pubsub
