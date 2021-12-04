use google_sheets4::{
    api::{AppendValuesResponse, Scope, ValueRange},
    Sheets,
};
use hyper::Client;
use hyper_rustls::HttpsConnector;
use yup_oauth2::{InstalledFlowAuthenticator, InstalledFlowReturnMethod};
use once_cell::sync::Lazy;

use std::path::PathBuf;

use crate::person::Person;

static TOKEN_STORAGE_PATH: Lazy<PathBuf> = Lazy::new(|| {
    let mut path = glib::user_data_dir();
    path.push("token_cache.json");
    path
});

pub struct Spreadsheet {
    id: String,
    hub: Sheets,
}

impl Spreadsheet {
    pub async fn new(id: &str, client_secret: &str) -> anyhow::Result<Self> {
        let client = Client::builder().build(HttpsConnector::with_native_roots());

        let app_secret = yup_oauth2::parse_application_secret(client_secret)?;
        let method = InstalledFlowReturnMethod::Interactive;
        let authenticator = InstalledFlowAuthenticator::builder(app_secret, method)
            .persist_tokens_to_disk(TOKEN_STORAGE_PATH.as_path())
            .hyper_client(client.clone())
            .build()
            .await?;

        let hub = Sheets::new(client, authenticator);

        Ok(Self {
            id: id.to_string(),
            hub,
        })
    }

    pub async fn append_person(&self, person: Person) -> anyhow::Result<AppendValuesResponse> {
        let range = "Sheet1!A1:F1"; // Single column for each `Person` field

        let request = ValueRange {
            major_dimension: None,
            range: None,
            values: Some(vec![person.into_vec()]),
        };

        let (body, response) = self
            .hub
            .spreadsheets()
            .values_append(request, self.id.as_str(), range)
            .add_scope(Scope::Spreadsheet)
            .value_input_option("USER_ENTERED")
            .doit()
            .await?;

        log::info!("Sucessfully appended person with body `{:?}`", body);

        Ok(response)
    }
}
