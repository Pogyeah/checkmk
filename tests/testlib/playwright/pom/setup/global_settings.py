# !/usr/bin/env python3
# Copyright (C) 2024 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import re
from urllib.parse import quote_plus

from playwright.sync_api import Locator

from tests.testlib.playwright.pom.page import CmkPage


class GlobalSettings(CmkPage):
    page_title: str = "Global settings"
    dropdown_buttons: list[str] = ["Related", "Display", "Help"]

    def navigate(self) -> None:
        _url_pattern = quote_plus("wato.py?mode=globalvars")
        self.main_menu.setup_menu(self.page_title).click()
        self.page.wait_for_url(re.compile(f"{_url_pattern}$"), wait_until="load")

    def _validate_page(self) -> None:
        self.main_area.check_page_title(self.page_title)

    @property
    def _searchbar(self) -> Locator:
        return self.main_area.locator().get_by_role(role="textbox", name="Find on this page ...")

    def setting_link(self, setting_name: str) -> Locator:
        return self.get_link(setting_name)

    def search_settings(self, search_text: str) -> None:
        """Search for a setting using the searchbar."""
        self._searchbar.fill(search_text)
        self.main_area.locator().get_by_role(role="button", name="Submit").click()
