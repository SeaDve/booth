import gi

gi.require_version("Gst", "1.0")
from gi.repository import Gst

from application import Application


def main():
    Gst.init(None)

    app = Application()
    app.run()


if __name__ == "__main__":
    main()
