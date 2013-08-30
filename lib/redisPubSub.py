import redis
import json
from operator import itemgetter, attrgetter 
from datetime import datetime

class RedisPubSub():

    def __init__(self, host='localhost', port=6379):
      self._rc = redis.StrictRedis(host, port, db=0)
      self._pubsub = self._rc.pubsub();



    """
        Data retrieval functions
    """

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

    "get all jobs belong to the host_name"
    def get_jobs(self, host_name):
        jobs = self.get_all_jobs()
        results = []

        for job_key in jobs:
            host_name_ = job_key.split(':')[0]
            if host_name_ == host_name:
              results.append(job_key)

        return results

    "get all builds belong to the host_name:job_name"
    def get_builds(self, host_name, job_name):
        results = {}
        builds = self.get_all_builds()

        for build_key in builds:
            host_name_ = build_key.split(':')[0]
            job_name_ = build_key.split(':')[1]

            if (host_name_ == host_name and job_name_ == job_name):
                build = self._rc.hgetall(build_key)
                results[build_key] = build

        return results

    "get a build belong to the host_name:job_name:build_number"
    def get_build(self, host_name, job_name, build_number):
        build = self._rc.hgetall(host_name+":"+job_name+":"+build_number)
        print build

        if ('test_result' in build and build['test_result']):
            test_data = json.loads(build['test_result']);
            build['test_result'] = test_data

        return build

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

    "return everything sorted based on certain field"
    def get_all_sorted(self, field, reverse=False, count=100):
        # get all builds limited by count
        # build_names = self._rc.smembers("builds")
        build_names = self._rc.zrange("sort:build_time_in_millis", 0, count)
        builds = []

        for build_name in build_names:
            build = self._rc.hgetall(build_name)
            # convert string to int
            build['build_number'] = int(build['build_number']) if ('build_number' in build) else None
            build['build_duration'] = int(build['build_duration']) if ('build_duration' in build) else None
            build['build_time_in_millis'] = int(build['build_time_in_millis']) if ('build_time_in_millis' in build) else None
            builds.append(build)

        return sorted(builds, key=itemgetter(field), reverse=reverse)

    def get_all_filtered_by_age(self, age, reverse=False):
        build_names = self._rc.zrange("sort:build_time_in_millis", 0, -1)
        builds = []

        for build_name in build_names:
            build = self._rc.hgetall(build_name)
            # convert string to int
            build['build_number'] = int(build['build_number']) if ('build_number' in build) else None
            build['build_duration'] = int(build['build_duration']) if ('build_duration' in build) else None
            build['build_time_in_millis'] = int(build['build_time_in_millis']) if ('build_time_in_millis' in build) else None
            build_time = datetime.utcfromtimestamp(build['build_time_in_millis']/1000)
            now = datetime.utcnow()

            if ( (now - build_time).days <= age):
                builds.append(build)

        return sorted(builds, key=itemgetter('build_time_in_millis'), reverse=reverse)

    def get_all_filtered_by_host(self, host, reverse=False):
        build_names = self._rc.keys(host+":*:*")
        builds = []

        for build_name in build_names:
            build = self._rc.hgetall(build_name)
            # convert string to int
            build['build_number'] = int(build['build_number']) if ('build_number' in build) else None
            build['build_duration'] = int(build['build_duration']) if ('build_duration' in build) else None
            build['build_time_in_millis'] = int(build['build_time_in_millis']) if ('build_time_in_millis' in build) else None
            builds.append(build)

        return sorted(builds, key=itemgetter('build_time_in_millis'), reverse=reverse)

    "list all keys in database, for debug purpose"
    def list_all_keys(self):
        hashes = self._rc.keys()
        return hashes



    """
        Sort functions
    """

    "list builds sorted by metric"
    def list_sorted_builds(self, limit, metric, desc=True, withscores=True):
        limit = int(limit) - 1
        temp = self._rc.zrange("sort:"+metric, 0, limit, desc, withscores)
        data = []
        for build, value in temp:
            # convert milli-seconds to seconds
            build_date = str(datetime.utcfromtimestamp(value/1000))
            data.append((build, build_date))

        return data

    "list builds sorted by duration"
    def list_builds_by_duration(self, limit, desc=True, withscores=True):
        limit = int(limit) - 1
        return self._rc.zrange("sort:build_duration", 0, limit, desc, withscores)

    "list builds sorted by scheduled time"
    def list_builds_by_time(self, limit, desc=True, withscores=True):
        return self.list_sorted_builds(limit, "build_time_in_millis", desc, withscores)

    # not working yet because yhudson does not support scheduled time
    "list builds sorted by scheduled time"
    def list_builds_by_start_time(self, limit, desc=True, withscores=True):
        return self.list_sorted_builds(limit, "build_start_time_in_millis", desc, withscores)

    "list successful builds sorted by scheduled time"
    def list_successful_builds(self, limit, desc=True, withscores=True):
        return self.list_sorted_builds(limit, "SUCCESS", desc, withscores)

    "list failed builds sorted by scheduled time"
    def list_failed_builds(self, limit, desc=True, withscores=True):
        return self.list_sorted_builds(limit, "FAILURE", desc, withscores)

    "list aborted builds sorted by scheduled time"
    def list_aborted_builds(self, limit, desc=True, withscores=True):
        return self.list_sorted_builds(limit, "ABORTED", desc, withscores)

    "list not built builds sorted by scheduled time"
    def list_not_built_builds(self, limit, desc=True, withscores=True):
        return self.list_sorted_builds(limit, "NOT_BUILT", desc, withscores)

    "list unstable builds sorted by scheduled time"
    def list_unstable_builds(self, limit, desc=True, withscores=True):
        return self.list_sorted_builds(limit, "UNSTABLE", desc, withscores)



    """
        Count functions
    """

    def count_hosts(self):
        return self._rc.scard("hosts")

    def count_jobs(self):
        return self._rc.scard("jobs")

    def count_builds(self):
        return self._rc.scard("builds")

    def count_channels(self):
        return self._rc.scard("jobs")

    def count_failed_builds(self):
        return self._rc.zcard("sort:FAILURE")

    def count_successful_builds(self):
        return self._rc.zcard("sort:SUCCESS")

    def count_aborted_builds(self):
        return self._rc.zcard("sort:ABORTED")

    def count_not_built_builds(self):
        return self._rc.zcard("sort:NOT_BUILT")

    def count_unstable_builds(self):
        return self._rc.zcard("sort:UNSTABLE")

    # not implemented yet because it is only supported since Redis 2.8
    # will implement it after Redis 2.8.0-rc1 becomes official
    "Count active channels. Active channels are those subscribed by users."
    def count_active_channels(self, pattern):
        return self._pubsub.execute_command("PUBSUB CHANNELS", pattern)


    """
        Pub/Sub functions
    """

    def subscribe(self, channel_name):
        return self._pubsub.subscribe(channel_name)

    def psubscribe(self, channel_pattern):
        return self._pubsub.psubscribe(channel_pattern)

    def unsubscribe(self, channel_name):
        return self._pubsub.unsubscribe(channel_name)

    def punsubscribe(self, channel_pattern):
        if (channel_pattern is None):
            return self._pubsub.punsubscribe()
        else:
            return self._pubsub.punsubscribe(channel_pattern)

    def listen(self):
        return self._pubsub.listen()

    def publish(self, channel, message):
        return self._rc.publish(channel, message)

    def disconnect(self):
        return self._rc.connection_pool.disconnect()


    """
      Return a pubsub instance that can be listened on.
      It should not be called unless you want to manually manage the subscription and
      publishing.
    """
    def pubsub(self):
        return self._pubsub
