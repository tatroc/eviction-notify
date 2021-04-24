#!/usr/bin/python3
from datetime import datetime
import json
import time
import urllib.request
import urllib.parse
import base64
import syslog
import os
jenkins = True
debug = True

username = os.getenv('JENKINS_USERNAME')
password = os.getenv('JENKINS_PASSWORD')
jenkins_uri = os.getenv('JENKINS_URI')



if debug == True:
    syslog.syslog(syslog.LOG_INFO, str(jenkins_uri))



def metadata(myinterval):
    HEADERS = {"Metadata":"true"}

    req = urllib.request.Request("http://169.254.169.254/metadata/instance?api-version=2020-09-01", headers=HEADERS)
    resp = urllib.request.urlopen(req)
    body = resp.read()
    metadata_obj = json.loads(body)
    print(metadata_obj['compute']['name'])
    print(metadata_obj['compute']['resourceGroupName'])
    print(metadata_obj['compute']['subscriptionId'])
    print(body)

    while True:

        print(datetime.now().__str__() + ' : Start Metadata task in the background')

        req = urllib.request.Request("http://169.254.169.254/metadata/scheduledevents?api-version=2019-01-01", headers=HEADERS)
        resp = urllib.request.urlopen(req)
        body = resp.read()
        json_event_obj = json.loads(body)
        print(body)
        if debug == True:
            syslog.syslog(syslog.LOG_INFO, str(body))
        message_sent = False
        for e in json_event_obj['Events']:
            EVENT = []
            now = datetime.utcnow()
            print(e['EventType'])
            date_time_str = e['NotBefore']
            date_time_obj = datetime.strptime(date_time_str, '%a, %d %b %Y  %H:%M:%S GMT')
            date_time_obj.utcnow
            diff = date_time_obj - now
            print('Now: ' + str(now))
            print('vmShutdownTime: ' + str(date_time_obj))
            print('Shutting down in: ' + str(diff.seconds) + " seconds!!!")
            syslog.syslog(syslog.LOG_INFO, 'Shutting down in: ' + str(diff.seconds) + " seconds!!!")
            if diff.seconds < 5:
                if 'Preempt' in str(json_event_obj['Events']):
                    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
                    resp_message = {
                        "message" : "Spot instance evicted, shutting down in: " + str(diff) + ' seconds',
                        "timestamp" : date_time
                    }
                    params = urllib.parse.urlencode({'subscription_id':metadata_obj['compute']['subscriptionId'], 'resource_group': metadata_obj['compute']['resourceGroupName'], 'name': metadata_obj['compute']['name']})

                    username_password = username + ':' + password

                    base64string = str(base64.b64encode(bytes(username_password, 'utf-8')).decode("utf-8") )
                    print("Calling Jenkins URL : " + jenkins_uri + params)
  
                    syslog.syslog(syslog.LOG_INFO, "Calling Jenkins URL : " + jenkins_uri + params)
                    JENKINS_HEADER = {"Authorization":"Basic %s" % base64string}
                    req = urllib.request.Request(jenkins_uri + params, headers=JENKINS_HEADER, method='POST')
                    resp = urllib.request.urlopen(req)
                    body = resp.read()
                    print(body)

                    print(json.dumps(resp_message))
                    syslog.syslog(syslog.LOG_INFO, json.dumps(resp_message))

            else:

                print('Delaying message send.')


        time.sleep(myinterval)

if __name__ == "__main__":
    metadata(1)