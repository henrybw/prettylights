#!/usr/bin/env python
import argparse
import array
from collections import deque
import functools
import random
import sys
import time
import phue
import pyaudio
import secrets

SAMPLE_WIDTH_BYTES = 2
CHANNELS = 2
SAMPLE_RATE_HZ = 44100
LIGHT_DIM = 5
LIGHT_SPOT = 255

class table(dict):
    def __init__(self, **kwargs):
        super(table, self).__init__(**kwargs)
        self.__dict__ = self

class stream_context(table):
    prev_time = 0

def stream_got_data(sctx, data, num_frame, time_info, status):
    current_time = time_info['current_time']
    if not sctx.prev_time:
        sctx.prev_time = current_time
        return (None, pyaudio.paContinue)

    dt = current_time - sctx.prev_time
    sctx.prev_time = current_time

    pwm_data = array.array("h")
    pwm_data.fromstring(data)

    # TODO well the pwm data seems to be accurate... so i guess we should
    # start applying the mathematics here...

    return (None, pyaudio.paContinue)

def init_lights(bridge, group):
    scene = scenes_by_name["Dope"]  # hehehe
    bridge.activate_scene(group.group_id, scene.scene_id)

    for light in group.lights:
        light.brightness = LIGHT_DIM

def find_group(args, bridge):
    group_id = int(args.group_id if args.group_id else
                   bridge.get_group_id_by_name(args.group_name))
    matches = [g for g in bridge.groups if g.group_id == group_id]
    assert len(matches) == 1
    group = matches[0]
    return group

def verify_light_config(args, bridge, parser):
    if args.list_groups:
        for g in bridge.groups:
            print "group_id: %d, name: %s" % (g.group_id, g.name)
        sys.exit(0)

    if not (args.group_id or args.group_name):
        print "need to specify a group"
        parser.print_help()
        sys.exit(1)

def create_parser():
    parser = argparse.ArgumentParser(
        description="Music visualizer that generates changing colors over "
        "time. Developed to implement a music visualizer on a group of Philips "
        "Hue programmable lightbulbs."
    )
    opts = parser.add_mutually_exclusive_group()
    opts.add_argument("-g", "--group", "--group-id", dest="group_id",
                      metavar='id', type=int, help="id of group to control")
    opts.add_argument("-N", "--name", "--group-name", dest="group_name",
                      metavar='name', help="name of group to control")
    opts.add_argument("-l", "--list", "--list-groups", dest="list_groups",
                      help="list all available groups and exit",
                      action="store_true")
    opts.add_argument("-n", "--no-lights", "--dry-run", dest="use_lights",
                      help="process microphone data without affecting lights",
                      action="store_false")
    return parser

def main():
    parser = create_parser()
    args = parser.parse_args()
    pactx = pyaudio.PyAudio()

    if args.use_lights:
        bridge = phue.Bridge(secrets.HUE_BRIDGE, username=secrets.HUE_TOKEN)
        verify_light_config(args, bridge, parser)
        group = find_group(args, bridge)
        init_lights(bridge, group)

    sctx = stream_context()
    stream = pactx.open(
        format=pactx.get_format_from_width(SAMPLE_WIDTH_BYTES, unsigned=False),
        channels=CHANNELS, rate=SAMPLE_RATE_HZ,
        input=True, output=False,
        stream_callback=functools.partial(stream_got_data, sctx)
    )
    stream.start_stream()

    try:
        if args.use_lights:
            last_light = None
            light_queue = deque(group.lights)

        while stream.is_active():
            if args.use_lights:
                light = light_queue.popleft()
                if not light_queue:
                    light_queue.extend(group.lights)

                if last_light:
                    last_light.brightness = LIGHT_DIM
                last_light = light

                light.brightness = LIGHT_SPOT

            time.sleep(0.25)
    except KeyboardInterrupt:
        pass

    stream.stop_stream()
    stream.close()

    pactx.terminate()

if __name__ == "__main__":
    main()
