# prettylights
Light show color mixer for a group of Philips Hue programmable lightbulbs.

# Setup

Tools:

* [Git](https://git-scm.com/) (which you needed to clone this repository)
* [Python](https://www.python.org/)

Libraries:

* [phue](https://github.com/studioimaginaire/phue)
* [PortAudio](http://www.portaudio.com)
* [PyAudio](https://people.csail.mit.edu/hubert/pyaudio/)
* [FFTW](http://www.fftw.org)
* [pyFFTW](https://pypi.python.org/pypi/pyFFTW)

## Mac OS X

    $ brew install portaudio fftw
    $ pip install phue pyaudio pyfftw

## Ubuntu

    # apt-get install libfftw3-dev python-pyaudio
    # pip install phue pyfftw

## Arch Linux

    # pacman -S portaudio fftw
    # pip install phue pyaudio pyfftw

## Secrets

If you try to run prettylights immediately, you'll notice that it will fail
because it cannot find the `secrets` module. For access security, all operations
exposed by the Philips Hue API require a "username" token, which is obtained by
physically authenticating with the bridge first (i.e. requesting credentials
from the bridge, and pressing a button on the bridge to confirm physical
access). See the [getting started guide][1] for more details about this process.

In order to use this access token with prettylights, create a new file in the
repository called `secrets.py`, and define the following constants:

    HUE_TOKEN="your-api-developer-username"
    HUE_BRIDGE="hue-bridge-ip-address"

This file is explicitly excluded from the repository (via .gitignore), to
prevent sensitive tokens from being pushed publicly.

[1]: https://developers.meethue.com/documentation/getting-started
