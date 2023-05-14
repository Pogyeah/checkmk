#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


from cmk.base.check_api import LegacyCheckDefinition
from cmk.base.check_legacy_includes.cisco_ucs import DETECT, map_operability
from cmk.base.config import check_info
from cmk.base.plugins.agent_based.agent_based_api.v1 import SNMPTree

# comNET GmbH, Fabian Binder - 2018-05-07

# .1.3.6.1.4.1.9.9.719.1.15.56.1.2  cucsEquipmentPsuDn
# .1.3.6.1.4.1.9.9.719.1.15.56.1.8  cucsEquipmentPsuOperability
# .1.3.6.1.4.1.9.9.719.1.15.56.1.13 cucsEquipmentPsuSerial
# .1.3.6.1.4.1.9.9.719.1.15.56.1.6  cucsEquipmentPsuModel


def inventory_cisco_ucs_psu(info):
    for name, _status, _serial, _model in info:
        name = name.split("/")[2]
        yield name, None


def check_cisco_ucs_psu(item, _no_params, info):
    for name, status, serial, model in info:
        name = name.split("/")[2]
        if name == item:
            state, state_readable = map_operability.get(
                status, (3, "Unknown, status code %s" % status)
            )
            return state, "Status: %s, Model: %s, SN: %s" % (state_readable, model, serial)
    return None


check_info["cisco_ucs_psu"] = LegacyCheckDefinition(
    detect=DETECT,
    check_function=check_cisco_ucs_psu,
    discovery_function=inventory_cisco_ucs_psu,
    service_name="PSU %s",
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.9.9.719.1.15.56.1",
        oids=["2", "8", "13", "6"],
    ),
)
