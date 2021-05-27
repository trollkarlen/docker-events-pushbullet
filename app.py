# Copyright 2018 Socialmetrix
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
import time
import signal

import docker

from pushbullet import Pushbullet

pb_key = None
event_filters = ["create", "update", "destroy", "die", "kill", "pause", "unpause", "start", "stop"]
events = ["create", "update", "destroy", "die", "kill", "pause", "unpause", "start", "stop"]
event_ending = {"create": "d", "update": "d", "destroy": "ed", "die": "d", "kill": "ed",
                "pause": "d", "unpause": "d", "start": "ed", "stop": "ed"}
ignore_names = []

BUILD_VERSION = os.getenv('BUILD_VERSION')
APP_NAME = 'Docker Events PushBullet (v{})'.format(BUILD_VERSION)

def get_config(env_key, optional=False):
    value = os.getenv(env_key)
    if not value and not optional:
        print('Environment variable {} is missing. Can\'t continue'.format(env_key))
        sys.exit(1)
    return value


def watch_and_notify_events(client):

    e_filters = {"event": event_filters}

    for event in client.events(filters=e_filters, decode=True):
        # container_id = event['Actor']['ID'][:12]
        print(event)
        attributes = event['Actor']['Attributes']

        if attributes['name'] in ignore_names:
            continue

        when = time.strftime('%Y-%m-%d %H:%M:%S %Z', time.localtime(event['time']))

        if event['status'] in events:
            event['status past tense'] = event['status'] + event_ending[event['status']]
        else:
            print("Status not mapped, {}".format(event['status']))
            event['status past tense'] = event['status'] + 'd'

        if event['status'] in ['die'] and 'exitCode' in attributes:
            event['status past tense'] += " with exitcode {}".format(attributes['exitCode'])

        message = "The container {} ({}) {} at {}" \
            .format(attributes['name'],
                    attributes['image'],
                    event['status past tense'],
                    when)
        send_message(message)


def send_message(message):
    pb = Pushbullet(pb_key)
    pb.push_note("Docker Event", message)


def exit_handler(_signo, _stack_frame):
    send_message('{} received SIGTERM on {}. Goodbye!'.format(APP_NAME, host))
    sys.exit(0)


def host_server(client):
    return client.info()['Name']


if __name__ == '__main__':
    pb_key = get_config("PB_API_KEY")

    events_string = get_config("EVENTS", True)
    if events_string:
        event_filters = events_string.split(',')

    ignore_strings = get_config("IGNORE_NAMES", True)
    if ignore_strings:
        ignore_names = ignore_strings.split(',')

    signal.signal(signal.SIGTERM, exit_handler)
    signal.signal(signal.SIGINT, exit_handler)

    gclient = docker.DockerClient(base_url='unix://var/run/docker.sock')
    host = host_server(gclient)

    gmessage = '{} reporting for duty on {}'.format(APP_NAME, host)

    send_message(gmessage)

    watch_and_notify_events(gclient)
