use chrono::Local;
use gio::{prelude::*, subclass::prelude::*};
use glib::clone;
use once_cell::unsync::OnceCell;

use std::{cell::RefCell, time::Duration};

use crate::{camera::Camera, person::Person, utils};

mod imp {
    use super::*;

    #[derive(Debug, Default)]
    pub struct Application {
        pub camera: Camera,
        pub people: RefCell<Vec<Person>>,

        pub last_code: RefCell<String>,
        pub code_detected_handler_id: OnceCell<glib::SignalHandlerId>,
    }

    #[glib::object_subclass]
    impl ObjectSubclass for Application {
        const NAME: &'static str = "NwtyApplication";
        type Type = super::Application;
        type ParentType = gio::Application;
    }

    impl ObjectImpl for Application {}

    impl ApplicationImpl for Application {
        fn activate(&self, obj: &Self::Type) {
            self.parent_activate(obj);

            obj.on_activate();
        }

        fn startup(&self, obj: &Self::Type) {
            self.parent_startup(obj);

            obj.on_startup();
        }
    }
}

glib::wrapper! {
    pub struct Application(ObjectSubclass<imp::Application>)
        @extends gio::Application;
}

impl Application {
    pub fn new() -> Self {
        glib::Object::new(&[
            ("application-id", &Some("io.github.seadve.Booth")),
            ("flags", &gio::ApplicationFlags::empty()),
        ])
        .expect("Application initialization failed...")
    }

    fn block_camera_detection(&self) {
        let imp = imp::Application::from_instance(self);
        imp.camera
            .block_signal(imp.code_detected_handler_id.get().unwrap());
    }

    fn unblock_camera_detection(&self) {
        let imp = imp::Application::from_instance(self);
        imp.camera
            .unblock_signal(imp.code_detected_handler_id.get().unwrap());
    }

    fn on_activate(&self) {
        let imp = imp::Application::from_instance(self);

        if let Err(err) = imp.camera.start() {
            log::error!("Failed to start camera {:?}", err);
        }
    }

    fn on_startup(&self) {
        self.hold();

        let imp = imp::Application::from_instance(self);

        imp.code_detected_handler_id
            .set(
                imp.camera
                    .connect_code_detected(clone!(@weak self as obj => move |_, code| {
                        let code = code.to_string();

                        let ctx = glib::MainContext::default();
                        ctx.spawn_local(async move {
                            obj.on_camera_code_detected(&code).await;
                        })
                    })),
            )
            .unwrap();

        glib::timeout_add_seconds_local(
            5,
            clone!(@weak self as obj => @default-return Continue(false), move || {
                let imp = imp::Application::from_instance(&obj);
                imp.last_code.take();

                Continue(true)
            }),
        );
    }

    async fn on_camera_code_detected(&self, code: &str) {
        self.block_camera_detection();

        let imp = imp::Application::from_instance(self);

        if imp.last_code.borrow().as_str() == code {
            log::info!("Same code as last, returning...");
        } else {
            self.handle_code_detected(code).await;
        }

        self.unblock_camera_detection();
    }

    async fn handle_code_detected(&self, code: &str) {
        let current_time = Local::now();

        log::info!("Code detected: {}; Current time: {}", code, &current_time);

        let imp = imp::Application::from_instance(self);
        imp.last_code.replace(code.to_string());

        let mut code = String::from(code);
        code.push_str(&format!("\ntime_detected: {}", current_time.to_rfc3339()));

        // TODO actually get temp from sensor
        // Simulate sensor getting
        utils::sleep(Duration::from_secs(1)).await;
        code.push_str(&format!("\ntemperature: {}", 37.1));

        match Person::from_str(&code) {
            Ok(person) => imp.people.borrow_mut().push(person),
            Err(err) => log::warn!("Failed to parse string {}: {:?}", code, err),
        }
    }
}

impl Default for Application {
    fn default() -> Self {
        gio::Application::default()
            .unwrap()
            .downcast::<Application>()
            .unwrap()
    }
}
