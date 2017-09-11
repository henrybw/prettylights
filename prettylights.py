#!/usr/bin/env python
import phue
import secrets

def main():
    b = phue.Bridge(secrets.HUE_BRIDGE, username=secrets.HUE_TOKEN)
    for l in b.lights:
        print(l.name)

if __name__ == "__main__":
    main()
