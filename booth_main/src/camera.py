from gi.repository import GObject, Gst

from utils import log_error, log_info


class ElementNotFoundError(Exception):
    def __init__(self, element_name: str):
        self._element_name = element_name

    def __str__(self):
        return f"Element {self._element_name} not found"


class Camera(GObject.Object):
    __gsignals__ = {
        "code-detected": (GObject.SIGNAL_RUN_LAST, None, (str,)),
        "error": (GObject.SIGNAL_RUN_LAST, None, ()),
    }

    _pipeline: Gst.Pipeline = None
    _bus: Gst.Bus = None

    def __init__(self):
        super().__init__()

    def start(self):
        if self._pipeline is None:
            self._setup_pipeline()

        self._bus.add_signal_watch()
        self._bus_handler_id = self._bus.connect("message", self._handle_message)
        self._pipeline.set_state(Gst.State.PLAYING)
        log_info("Camera started")

    def stop(self):
        self._pipeline.set_state(Gst.State.NULL)
        self._bus.disconnect(self._bus_handler_id)
        self._bus.remove_signal_watch()

    def _handle_message(self, bus: Gst.Bus, message: Gst.Message) -> bool:
        if message.type == Gst.MessageType.ELEMENT:
            symbol = message.get_structure().get_value("symbol")
            if symbol is not None:
                self.emit("code-detected", symbol)
            return True

        if message.type == Gst.MessageType.STATE_CHANGED:
            if message.src == self._pipeline:
                old_state, new_state, pending = message.parse_state_changed()
                log_info(f"Pipeline state set from {old_state} -> {new_state}")
            return True

        if message.type == Gst.MessageType.ERROR:
            error, debug = message.parse_error()
            log_error(f"Error from message bus: {error} ({debug})")
            self.stop()
            self._pipeline = None
            self.emit("error")
            return False

        return True

    def _setup_pipeline(self) -> None:
        self._pipeline = Gst.parse_launch(
            "v4l2src ! video/x-raw, max-framerate=5/1 ! videoconvert ! zbar ! fakesink"
        )
        self._bus = self._pipeline.get_bus()


def make_gst_element(name: str) -> Gst.Element:
    element = Gst.ElementFactory.make(name)

    if element is None:
        raise ElementNotFoundError(name)

    return element
