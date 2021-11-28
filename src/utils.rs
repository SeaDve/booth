use std::{thread, time::Duration};

pub async fn sleep(duration: Duration) {
    let (sender, receiver) = futures_channel::oneshot::channel();

    thread::spawn(move || {
        thread::sleep(duration);
        sender.send(()).unwrap();
    });

    receiver.await.unwrap();
}
