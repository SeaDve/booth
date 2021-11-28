use anyhow::Context;
use gio::{prelude::*, subclass::prelude::*};
use glib::{clone, subclass::Signal};
use gst::prelude::*;
use once_cell::unsync::OnceCell;

mod imp {
    use super::*;

    #[derive(Debug, Default)]
    pub struct Camera {
        pub pipeline: OnceCell<gst::Pipeline>,
    }

    #[glib::object_subclass]
    impl ObjectSubclass for Camera {
        const NAME: &'static str = "BthCamera";
        type Type = super::Camera;
        type ParentType = glib::Object;
    }

    impl ObjectImpl for Camera {
        fn signals() -> &'static [Signal] {
            use once_cell::sync::Lazy;
            static SIGNALS: Lazy<Vec<Signal>> = Lazy::new(|| {
                vec![Signal::builder(
                    "code-detected",
                    &[String::static_type().into()],
                    <()>::static_type().into(),
                )
                .build()]
            });
            SIGNALS.as_ref()
        }

        fn constructed(&self, obj: &Self::Type) {
            self.parent_constructed(obj);

            if let Err(err) = obj.setup_pipeline() {
                log::error!("Failed to setup pipeline: {:#}", err);
            }
        }

        fn dispose(&self, _obj: &Self::Type) {
            self.pipeline
                .get()
                .unwrap()
                .set_state(gst::State::Null)
                .unwrap();
        }
    }
}

glib::wrapper! {
    pub struct Camera(ObjectSubclass<imp::Camera>);
}

impl Camera {
    pub fn new() -> Self {
        glib::Object::new(&[]).expect("Failed to create Camera.")
    }

    pub fn connect_code_detected<F>(&self, f: F) -> glib::SignalHandlerId
    where
        F: Fn(&Self, &str) + 'static,
    {
        self.connect_local("code-detected", true, move |values| {
            let obj = values[0].get::<Self>().unwrap();
            let code = values[1].get::<String>().unwrap();
            f(&obj, &code);
            None
        })
        .unwrap()
    }

    pub fn start(&self) -> anyhow::Result<()> {
        let imp = imp::Camera::from_instance(self);
        let pipeline = imp.pipeline.get().unwrap();

        let bus = pipeline.bus().unwrap();
        bus.add_watch_local(
            clone!(@weak self as obj => @default-return Continue(false), move |_, message| {
                obj.handle_bus_message(message)
            }),
        )
        .unwrap();

        pipeline
            .set_state(gst::State::Playing)
            .context("Failed to set pipeline state to Playing")?;

        Ok(())
    }

    pub fn stop(&self) -> anyhow::Result<()> {
        let imp = imp::Camera::from_instance(self);
        let pipeline = imp.pipeline.get().unwrap();

        pipeline.set_state(gst::State::Null)?;
        let bus = pipeline.bus().unwrap();
        bus.remove_watch()?;

        Ok(())
    }

    fn setup_pipeline(&self) -> anyhow::Result<()> {
        let pipeline = gst::Pipeline::new(None);

        let pipewiresrc = gst::ElementFactory::make("pipewiresrc", None)?;
        let queue = gst::ElementFactory::make("queue", None)?;
        let videoconvert = gst::ElementFactory::make("videoconvert", None)?;
        let zbar = gst::ElementFactory::make("zbar", None)?;
        let fakesink = gst::ElementFactory::make("fakesink", None)?;

        let elements = &[&pipewiresrc, &queue, &videoconvert, &zbar, &fakesink];
        pipeline.add_many(elements)?;
        gst::Element::link_many(elements)?;

        for e in elements {
            e.sync_state_with_parent()?;
        }

        let imp = imp::Camera::from_instance(self);
        imp.pipeline.set(pipeline).unwrap();

        Ok(())
    }

    fn handle_bus_message(&self, message: &gst::Message) -> Continue {
        use gst::MessageView;

        match message.view() {
            MessageView::Error(err) => {
                log::error!(
                    "Error from {:?}: {} ({:?})",
                    err.src().map(|s| s.path_string()),
                    err.error(),
                    err.debug()
                );

                self.stop().unwrap();

                Continue(false)
            }
            MessageView::StateChanged(sc) => {
                let imp = imp::Camera::from_instance(self);
                let pipeline = imp.pipeline.get().unwrap();

                if message.src().as_ref() == Some(pipeline.upcast_ref::<gst::Object>()) {
                    log::info!(
                        "Pipeline state set from {:?} -> {:?}",
                        sc.old(),
                        sc.current()
                    );
                }
                Continue(true)
            }
            MessageView::Element(e) => {
                let symbol: String = e.structure().unwrap().get("symbol").unwrap();

                self.emit_by_name("code-detected", &[&symbol]).unwrap();

                Continue(true)
            }
            _ => Continue(true),
        }
    }
}

impl Default for Camera {
    fn default() -> Self {
        Self::new()
    }
}
