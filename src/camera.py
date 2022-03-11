from gi.repository import GObject, Gst, GLib


class ElementNotFoundError(Exception):
    def __init__(self, element_name: str):
        self._element_name = element_name

    def __str__(self):
        return f"Element {self._element_name} not found"


class Camera(GObject.Object):
    __gsignals__ = {"code-detected": (GObject.SIGNAL_RUN_LAST, None, (str,))}

    _pipeline: Gst.Pipeline
    _bus: Gst.Bus

    def __init__(self):
        super().__init__()

        self._pipeline = Gst.Pipeline()
        self._bus = self._pipeline.get_bus()

        try:
            pipewiresrc = make_gst_element("pipewiresrc")
            queue = make_gst_element("queue")
            videoconvert = make_gst_element("videoconvert")
            zbar = make_gst_element("zbar")
            fakesink = make_gst_element("fakesink")
        except ElementNotFoundError as error:
            print(f"Error: {error}")

        elements = [pipewiresrc, queue, videoconvert, zbar, fakesink]

        for element in elements:
            self._pipeline.add(element)

        pipewiresrc.link(queue)
        queue.link(videoconvert)
        videoconvert.link(zbar)
        zbar.link(fakesink)

        for element in elements:
            element.sync_state_with_parent()

    def start(self):
        self._bus.add_signal_watch()
        self._bus_handler_id = self._bus.connect("message", self._handle_message)
        self._pipeline.set_state(Gst.State.PLAYING)
        print(">>> Camera started")

    def stop(self):
        self._pipeline.set_state(Gst.State.NULL)
        self._bus.disconnect(self._bus_handler_id)
        self._bus.remove_signal_watch()

    def _handle_message(self, bus: Gst.Bus, message: Gst.Message):
        if message.type == Gst.MessageType.ELEMENT:
            symbol = message.get_structure().get_value("symbol")
            if symbol is not None:
                self.emit("code-detected", symbol)
            return True

        if message.type == Gst.MessageType.STATE_CHANGED:
            if message.src == self._pipeline:
                old_state, new_state, pending = message.parse_state_changed()
                print(f">>> Pipeline state set from {old_state} -> {new_state}")
            return True

        if message.type == Gst.MessageType.ERROR:
            error, debug = message.parse_error()
            print(f"Error: {error} ({debug})")
            self.stop()
            return False


def make_gst_element(name: str) -> Gst.Element:
    element = Gst.ElementFactory.make(name)

    if element is None:
        raise ElementNotFoundError(name)

    return element
