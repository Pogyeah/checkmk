#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


from cmk.base.check_api import all_of, LegacyCheckDefinition, not_exists, startswith
from cmk.base.check_legacy_includes.akcp_sensor import check_akcp_humidity, inventory_akcp_humidity
from cmk.base.config import check_info
from cmk.base.plugins.agent_based.agent_based_api.v1 import SNMPTree

# Example for contents of info
#      description       percent  status  online
# ["Humdity1 Description", "0",    "0",    "2"]

check_info["akcp_sensor_humidity"] = LegacyCheckDefinition(
    detect=all_of(
        startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.3854.1"), not_exists(".1.3.6.1.4.1.3854.2.*")
    ),
    check_function=check_akcp_humidity,
    discovery_function=inventory_akcp_humidity,
    service_name="Humidity %s",
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.3854.1.2.2.1.17.1",
        oids=["1", "3", "4", "5"],
    ),
    check_ruleset_name="humidity",
)
