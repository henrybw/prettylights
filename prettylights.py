#!/usr/bin/env python
import argparse
import sys
import time
import phue
import secrets

def main():
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
    args = parser.parse_args()

    bridge = phue.Bridge(secrets.HUE_BRIDGE, username=secrets.HUE_TOKEN)

    if args.list_groups:
        for g in bridge.groups:
            print "group_id: %d, name: %s" % (g.group_id, g.name)
        sys.exit(0)

    if not (args.group_id or args.group_name):
        print "need to specify a group"
        parser.print_help()
        sys.exit(1)

    group_id = int(args.group_id if args.group_id else
                   bridge.get_group_id_by_name(args.group_name))
    matches = [g for g in bridge.groups if g.group_id == group_id]
    assert len(matches) == 1
    group = matches[0]

    scenes_by_name = {s.name: s for s in bridge.scenes}

    for light in group.lights:
        light.brightness = 5

    while True:
        for scene in scenes_by_name.values():
            bridge.activate_scene(group.group_id, scene.scene_id)

            last_light = None
            for light in group.lights:
                if last_light:
                    last_light.brightness = 5
                light.brightness = 255
                last_light = light
                time.sleep(2)

if __name__ == "__main__":
    main()
