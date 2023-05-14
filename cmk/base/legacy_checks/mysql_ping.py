#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


from cmk.base.check_api import discover, get_parsed_item_data, LegacyCheckDefinition
from cmk.base.check_legacy_includes.mysql import mysql_parse_per_item
from cmk.base.config import check_info

# <<<mysql_ping>>>
# [[instance]]
# mysqladmin: connect to server at 'localhost' failed
# error: 'Access denied for user 'root'@'localhost' (using password: NO)'
#


@get_parsed_item_data
def check_mysql_ping(_no_item, _no_params, data):
    message = " ".join(data[0])
    if message == "mysqld is alive":
        return 0, "MySQL Daemon is alive"
    return 2, message


check_info["mysql_ping"] = LegacyCheckDefinition(
    parse_function=mysql_parse_per_item(lambda info: info),
    discovery_function=discover(),
    check_function=check_mysql_ping,
    service_name="MySQL Instance %s",
)
