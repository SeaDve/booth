use chrono::{DateTime, Local};
use google_sheets4::api::ValueRange;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Person {
    name: String,
    address: String,
    contact_number: String,
    room_id: String,
    temperature: f32,
    time_detected: DateTime<Local>,
}

impl Person {
    pub fn from_str(string: &str) -> anyhow::Result<Self> {
        serde_yaml::from_str(string).map_err(Into::into)
    }

    pub fn into_value_range(self) -> ValueRange {
        ValueRange {
            major_dimension: None,
            range: Some("A1:F1".into()), // Single column for each field
            values: Some(vec![vec![
                self.name,
                self.address,
                self.contact_number,
                self.room_id,
                self.temperature.to_string(),
                self.time_detected.to_rfc3339(),
            ]]),
        }
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
        assert!((person.temperature - 36.7).abs() < f32::EPSILON);

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
        assert!((person.temperature - 36.7).abs() < f32::EPSILON);

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
