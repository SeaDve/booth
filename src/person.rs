use chrono::{DateTime, Local};

use std::collections::HashMap;

#[derive(Debug)]
pub struct Person {
    name: String,
    address: String,
    contact_number: String,
    room_id: String,
    temperature: f64,
    time_detected: DateTime<Local>,
}

impl Person {
    pub fn from_str(string: &str) -> anyhow::Result<Self> {
        let mut data = HashMap::new();

        for line in string.lines() {
            if line.contains("name:") {
                let name = line.trim().trim_start_matches("name:").trim();
                data.insert("name", name);
                continue;
            }

            if line.contains("address:") {
                let address = line.trim().trim_start_matches("address:").trim();
                data.insert("address", address);
                continue;
            }

            if line.contains("contact_number:") {
                let contact_number = line.trim().trim_start_matches("contact_number:").trim();
                data.insert("contact_number", contact_number);
                continue;
            }

            if line.contains("room_id:") {
                let room_id = line.trim().trim_start_matches("room_id:").trim();
                data.insert("room_id", room_id);
                continue;
            }

            if line.contains("temperature:") {
                let temperature = line.trim().trim_start_matches("temperature:").trim();
                data.insert("temperature", temperature);
                continue;
            }

            if line.contains("time_detected:") {
                let time_detected = line.trim().trim_start_matches("time_detected:").trim();
                data.insert("time_detected", time_detected);
                continue;
            }
        }

        let name = data.get("name").ok_or(anyhow::anyhow!("No name found"))?;
        let address = data
            .get("address")
            .ok_or(anyhow::anyhow!("No address found"))?;
        let contact_number = data
            .get("contact_number")
            .ok_or(anyhow::anyhow!("No contact_number found"))?;
        let room_id = data
            .get("room_id")
            .ok_or(anyhow::anyhow!("No room_id found"))?;
        let temperature = data
            .get("temperature")
            .ok_or(anyhow::anyhow!("No temperature found"))?;
        let time_detected = data
            .get("time_detected")
            .ok_or(anyhow::anyhow!("No time_detected found"))?;

        Ok(Self {
            name: name.to_string(),
            address: address.to_string(),
            contact_number: contact_number.to_string(),
            room_id: room_id.to_string(),
            temperature: temperature.parse().unwrap(),
            time_detected: DateTime::parse_from_rfc3339(time_detected)?.into(),
        })
    }
}

#[cfg(test)]
mod test {
    use super::*;

    #[test]
    fn from_str_ok_1() {
        let string = r#"
        name: Juan Dela Cruz
        address: Sa tabi-tabi
        contact_number: 09123345678
        room_id: Room123
        temperature: 36.7
        time_detected: 2018-01-26T18:30:09.453+00:00
        "#;

        let person = Person::from_str(string).unwrap();

        assert_eq!(person.name, "Juan Dela Cruz");
        assert_eq!(person.address, "Sa tabi-tabi");
        assert_eq!(person.contact_number, "09123345678");
        assert_eq!(person.room_id, "Room123");
        assert_eq!(person.temperature, 36.7);

        let expected_time_detected: DateTime<Local> =
            DateTime::parse_from_rfc3339("2018-01-26T18:30:09.453+00:00")
                .unwrap()
                .into();
        assert_eq!(person.time_detected, expected_time_detected);
    }

    #[test]
    fn from_str_ok_2() {
        let string = r#"
        time_detected: 2018-01-26T18:30:09.453+00:00
        name: Juan Dela Cruz
        contact_number: 09123345678
        temperature: 36.7
        room_id: Room123
        address: Sa tabi-tabi
        "#;

        let person = Person::from_str(string).unwrap();

        assert_eq!(person.name, "Juan Dela Cruz");
        assert_eq!(person.address, "Sa tabi-tabi");
        assert_eq!(person.contact_number, "09123345678");
        assert_eq!(person.room_id, "Room123");
        assert_eq!(person.temperature, 36.7);

        let expected_time_detected: DateTime<Local> =
            DateTime::parse_from_rfc3339("2018-01-26T18:30:09.453+00:00")
                .unwrap()
                .into();
        assert_eq!(person.time_detected, expected_time_detected);
    }

    #[test]
    #[should_panic]
    fn from_str_bad_1() {
        let string = r#"
        address: Sa tabi-tabi
        contact_number: 09123345678
        temperature: 36.7
        room_id: Room123
        time_detected: 2018-01-26T18:30:09.453+00:00
        "#;

        Person::from_str(string).unwrap();
    }

    #[test]
    #[should_panic]
    fn from_str_bad_2() {
        let string = r#"
        name: Juan Dela Cruz
        address: Sa tabi-tabi
        contact_number: 09123345678
        room_id: Room123
        time_detected: 2018-01-2618:30:09.453+00:00
        temperature: 36.7
        "#;

        Person::from_str(string).unwrap();
    }
}
