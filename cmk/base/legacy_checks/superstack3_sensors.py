#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


from cmk.base.check_api import contains, LegacyCheckDefinition
from cmk.base.config import check_info
from cmk.base.plugins.agent_based.agent_based_api.v1 import SNMPTree


def inventory_superstack3_sensors(info):
    return [(line[0], None) for line in info if line[1] != "not present"]


def check_superstack3_sensors(item, params, info):
    for name, state in info:
        if name == item:
            if state == "failure":
                return (2, "status is %s" % state)
            if state == "operational":
                return (0, "status is %s" % state)
            return (1, "status is %s" % state)
    return (3, "UNKOWN - sensor not found")


check_info["superstack3_sensors"] = LegacyCheckDefinition(
    detect=contains(".1.3.6.1.2.1.1.1.0", "3com superstack 3"),
    check_function=check_superstack3_sensors,
    discovery_function=inventory_superstack3_sensors,
    service_name="%s",
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.43.43.1.1",
        oids=["7", "10"],
    ),
)
