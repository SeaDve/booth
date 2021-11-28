mod application;
mod camera;
mod person;
mod utils;

use gio::prelude::*;

use self::application::Application;

fn main() {
    pretty_env_logger::init_timed();

    gst::init().expect("Unable to start GStreamer");

    let app = Application::new();
    app.run();
}
