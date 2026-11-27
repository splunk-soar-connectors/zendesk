# Copyright (c) 2026 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from soar_sdk.abstract import SOARClient
from soar_sdk.app import App
from soar_sdk.logging import getLogger

from .actions import register_actions
from .asset import Asset
from .helper import request as zendesk_request

logger = getLogger()


app = App(
    name="Zendesk",
    app_type="ticketing",
    logo="logo_zendesk.svg",
    logo_dark="logo_zendesk_dark.svg",
    product_vendor="Zendesk",
    product_name="Zendesk",
    publisher="Splunk",
    appid="c4478686-00ec-4a37-9c1f-f16f83abcf18",
    fips_compliant=True,
    encrypt_cache_state=True,
    encrypt_ingest_state=True,
    asset_cls=Asset,
)


@app.test_connectivity()
def test_connectivity(soar: SOARClient, asset: Asset) -> None:
    zendesk_request(asset, "GET", "/tickets/recent.json", params={"per_page": 1})
    soar.set_message("Connectivity test passed")


register_actions(app)


if __name__ == "__main__":
    app.cli()
