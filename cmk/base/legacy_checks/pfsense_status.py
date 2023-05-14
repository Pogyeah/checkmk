#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


from cmk.base.check_api import contains, LegacyCheckDefinition
from cmk.base.config import check_info
from cmk.base.plugins.agent_based.agent_based_api.v1 import SNMPTree


def inventory_pfsense_status(info):
    if info:
        return [(None, None)]
    return []


def check_pfsense_status(_no_item, params, info):
    statusvar = info[0][0]
    if statusvar == "1":
        return 0, "Running"
    if statusvar == "2":
        return 2, "Not running"

    raise Exception("Unknown status value %s" % statusvar)


check_info["pfsense_status"] = LegacyCheckDefinition(
    detect=contains(".1.3.6.1.2.1.1.1.0", "pfsense"),
    discovery_function=inventory_pfsense_status,
    check_function=check_pfsense_status,
    service_name="pfSense Status",
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.12325.1.200.1.1",
        oids=["1"],
    ),
)
