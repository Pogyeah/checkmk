#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


from cmk.base.check_api import check_levels, discover, get_parsed_item_data, LegacyCheckDefinition
from cmk.base.check_legacy_includes.quanta import parse_quanta
from cmk.base.config import check_info
from cmk.base.plugins.agent_based.agent_based_api.v1 import SNMPTree
from cmk.base.plugins.agent_based.utils.quanta import DETECT_QUANTA

# .1.3.6.1.4.1.7244.1.2.1.3.5.1.1.14 14
# .1.3.6.1.4.1.7244.1.2.1.3.5.1.1.15 15
# ...
# .1.3.6.1.4.1.7244.1.2.1.3.5.1.2.14 3
# .1.3.6.1.4.1.7244.1.2.1.3.5.1.2.15 3
# ...
# .1.3.6.1.4.1.7244.1.2.1.3.5.1.3.14 Volt_VR_DIMM_GH
# .1.3.6.1.4.1.7244.1.2.1.3.5.1.3.15 "56 6F 6C 74 5F 53 41 53 5F 45 58 50 5F 30 56 39 01 "
# ...
# .1.3.6.1.4.1.7244.1.2.1.3.5.1.4.14 1220
# .1.3.6.1.4.1.7244.1.2.1.3.5.1.4.15 923
# ...
# .1.3.6.1.4.1.7244.1.2.1.3.5.1.6.14 1319
# .1.3.6.1.4.1.7244.1.2.1.3.5.1.6.15 988
# ...
# .1.3.6.1.4.1.7244.1.2.1.3.5.1.7.14 -99
# .1.3.6.1.4.1.7244.1.2.1.3.5.1.7.15 -99
# ...
# .1.3.6.1.4.1.7244.1.2.1.3.5.1.8.14 -99
# .1.3.6.1.4.1.7244.1.2.1.3.5.1.8.15 -99
# ...
# .1.3.6.1.4.1.7244.1.2.1.3.5.1.9.14 1079
# .1.3.6.1.4.1.7244.1.2.1.3.5.1.9.15 806


@get_parsed_item_data
def check_quanta_voltage(item, params, entry):
    yield entry.status[0], "Status: %s" % entry.status[1]

    if entry.value in (-99, None):
        return

    yield check_levels(
        entry.value,
        "voltage",
        params.get("levels", entry.upper_levels) + params.get("levels_lower", entry.lower_levels),
        unit="V",
    )


check_info["quanta_voltage"] = LegacyCheckDefinition(
    detect=DETECT_QUANTA,
    discovery_function=discover(),
    parse_function=parse_quanta,
    check_function=check_quanta_voltage,
    service_name="Voltage %s",
    check_ruleset_name="voltage",
    # these is no good oid identifier for quanta devices, thats why the first oid is used here
    fetch=[
        SNMPTree(
            base=".1.3.6.1.4.1.7244.1.2.1.3.5.1",
            oids=["1", "2", "3", "4", "6", "7", "8", "9"],
        )
    ],
)
