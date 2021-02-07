# adafruit-pi-cam

A fork/update of the original `adafruit-pi-cam` project by
By PaintYourDragon (Phil B) for Adafruit Industries

The original instructions can be found at 
http://learn.adafruit.com/diy-wifi-raspberry-pi-touch-cam

## Installation notes

Installing this package will create the `adapicam` command in your path.

Python 3.6+ is required.

### Pygame
This project requires PyGame 1.9.X. (PyGame 2.0 uses LibSDL 2.0, which does not appear to work with PiTFTs).

In Raspbian, install pygame 1.9 from the distro repos *before* installing this program (the pygame 1.9.4 wheel in pypi will not work):

```
sudo apt-get install python3-pygame=1.9.4.post1
```

## Usage

See `adapicam --help`.


## Changes from the original project
 - capacitative touchscreen support
 - installable as python package (with pinned dependency versions)
 - appears to work with Raspbian's LibSDL 1.2 without having to download a special version (?)
 - \*lots\* of unnecessary refactoring, including a unidirectional data flow model
 - python 3.6+ required

## License
Most of this code remains under the original BSD 2-clause license.

The driver for capacitative touchscreens has been vendored from https://github.com/pigamedrv/pitft_touchscreen and is provided under GPL v3.