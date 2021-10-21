// Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
// This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
// conditions defined in the file COPYING, which is part of this source code package.

use reqwest;
use serde::Deserialize;

#[derive(Deserialize)]
struct JSONResponse {
    message: String,
}

pub fn register(_server_address: &str, _csr: Vec<u8>) -> reqwest::Result<String> {
    return Ok(String::from("Fake certificate for "));
}

pub fn agent_data(
    server_address: &str,
    uuid: &str,
    monitoring_data: Vec<u8>,
) -> reqwest::Result<String> {
    return Ok(reqwest::blocking::Client::new()
        .post(server_address.to_string() + "/agent-data")
        .multipart(
            reqwest::blocking::multipart::Form::new()
                .text("uuid", uuid.to_string())
                .part(
                    "upload_file",
                    reqwest::blocking::multipart::Part::bytes(monitoring_data)
                        // Note: We need to set the file name, otherwise the request won't have the
                        // right format. However, the value itself does not matter.
                        .file_name("agent_data"),
                ),
        )
        .send()?
        .json::<JSONResponse>()?
        .message);
}
