from redisSubPub import RedisSubPub
import threading

rsp = RedisSubPub()

def main():
    "list all channels"
    channels = rsp.list_all_channels()
    channel_count = rsp.count_channels()
    print "%d channels:"%channel_count
    for channel in channels:
        print(channel)

    hosts = rsp.get_all_hosts()
    host_count = rsp.count_hosts()
    print host_count, "hosts:"
    for host in hosts:
        print(host)

    jobs = rsp.get_all_jobs()
    job_count = rsp.count_jobs()
    print job_count, "jobs:"
    for job in jobs:
        print(job)

    builds = rsp.get_all_builds()
    build_count = rsp.count_builds()
    print build_count, "builds:"
    for build in builds:
        print(build)

    print "The jobs of notioncommotion.corp.gq1.yahoo.com are:"
    jobs = rsp.get_jobs("notioncommotion.corp.gq1.yahoo.com")
    for job in jobs:
      print job

    print "The builds of %s are:"%job
    host_name = job.split(':')[0]
    job_name = job.split(':')[1]
    builds = rsp.get_builds(host_name, job_name)
    for key, value in builds.items():
      print key
      print value
    
    print "there are active channels:"
    print rsp.count_active_channels

    limit = 50
    sortByDuration = rsp.list_builds_by_duration(limit)
    print "Longest %d builds:"%limit
    for build, duration in sortByDuration:
      print build, duration

    sortByTime = rsp.list_builds_by_time(limit)
    print "Lastest %d builds sorted by scheduled time:"%limit
    for build, duration in sortByTime:
      print build, duration

    sortByStartTime = rsp.list_builds_by_start_time(limit)
    print "Lastest %d builds sorted by start time:"%limit
    for build, duration in sortByStartTime:
      print build, duration

    limit = rsp.count_successful_builds()
    sortByStartTime = rsp.list_successful_builds(limit)
    print "%d successful builds sorted by start time:"%limit
    for build, duration in sortByStartTime:
      print build, duration

    limit = rsp.count_failed_builds()
    sortByStartTime = rsp.list_failed_builds(limit)
    print "%d failed builds sorted by start time:"%limit
    for build, duration in sortByStartTime:
      print build, duration

    limit = rsp.count_aborted_builds()
    sortByStartTime = rsp.list_aborted_builds(limit)
    print "%d aborted builds sorted by start time:"%limit
    for build, duration in sortByStartTime:
      print build, duration

    limit = rsp.count_not_built_builds()
    sortByStartTime = rsp.list_not_built_builds(limit)
    print "%d not built builds sorted by start time:"%limit
    for build, duration in sortByStartTime:
      print build, duration

    limit = rsp.count_unstable_builds()
    sortByStartTime = rsp.list_unstable_builds(limit)
    print "%d unstable builds sorted by start time:"%limit
    for build, duration in sortByStartTime:
      print build, duration


    """
    print("All data:")
    all_data = rsp.get_all()
    print all_data
    """

if __name__ == "__main__":
    main()
