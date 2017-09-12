#!/usr/bin/env python
import array
import argparse
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

def mic_callback(bin_data, frame_count, time_info, status):
    pwm_data = array.array("h")
    pwm_data.fromstring(bin_data)

    # TODO well the pwm data seems to be accurate... so i guess we should
    # start applying the mathematics here...

    return (pwm_data, pyaudio.paContinue)

def init_lights(group):
    for light in group.lights:
        light.brightness = LIGHT_DIM

def find_group(args, bridge):
    group_id = int(args.group_id if args.group_id else
                   bridge.get_group_id_by_name(args.group_name))
    matches = [g for g in bridge.groups if g.group_id == group_id]
    assert len(matches) == 1
    group = matches[0]
    return group

def handle_args(args, bridge, parser):
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
    opts.add_argument("-g", "--group", "--id", dest="group_id",
                    metavar='id', type=int, help="id of group to control")
    opts.add_argument("-n", "--name", "--group-name", dest="group_name",
                    metavar='name', help="name of group to control")
    opts.add_argument("-l", "--list", "--list-groups", dest="list_groups",
                    help="list all available groups and exit",
                    action="store_true")
    return parser

def main():
    parser = create_parser()
    args = parser.parse_args()
    bridge = phue.Bridge(secrets.HUE_BRIDGE, username=secrets.HUE_TOKEN)
    pactx = pyaudio.PyAudio()

    handle_args(args, bridge, parser)
    group = find_group(args, bridge)
    scenes_by_name = {s.name: s for s in bridge.scenes}

    init_lights(group)

    stream = pactx.open(
        format=pactx.get_format_from_width(SAMPLE_WIDTH_BYTES, unsigned=False),
        channels=CHANNELS,
        rate=SAMPLE_RATE_HZ,
        input=True,
        output=True,
        stream_callback=mic_callback
    )
    stream.start_stream()

    try:
        while stream.is_active():
            scene = scenes_by_name["Dope"]  # hehehe
            bridge.activate_scene(group.group_id, scene.scene_id)

            last_light = None
            for light in group.lights:
                if last_light:
                    last_light.brightness = LIGHT_DIM

                light.hue = random.randint(0, 255)
                light.saturation = random.randint(0, 255)
                light.brightness = LIGHT_SPOT

                last_light = light
                time.sleep(0.25)
    except KeyboardInterrupt:
        pass

    stream.stop_stream()
    stream.close()

    pactx.terminate()

if __name__ == "__main__":
    main()
