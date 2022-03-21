import RPi.GPIO as GPIO

import gi

gi.require_version("Gst", "1.0")
from gi.repository import Gst

from application import Application


def main():
    Gst.init(None)

    GPIO.setmode(GPIO.BCM)

    app = Application()

    print(">>> Application ran")
    app.run()

    GPIO.cleanup()


if __name__ == "__main__":
    main()
