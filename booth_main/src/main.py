import RPi.GPIO as GPIO

import gi

gi.require_version("Gst", "1.0")
from gi.repository import Gst

from application import Application
from utils import log_info


def main():
    Gst.init(None)

    GPIO.setmode(GPIO.BCM)

    app = Application()

    log_info("Application is now running")
    app.run()

    GPIO.cleanup()


if __name__ == "__main__":
    main()
