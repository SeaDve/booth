mod application;
mod camera;
mod person;
mod spreadsheet;

use gio::prelude::*;
use once_cell::sync::Lazy;

use self::application::Application;

static RUNTIME: Lazy<tokio::runtime::Runtime> =
    Lazy::new(|| tokio::runtime::Runtime::new().unwrap());

fn main() {
    pretty_env_logger::init_timed();

    gst::init().expect("Unable to start GStreamer");

    let app = Application::new();
    app.run();
}
