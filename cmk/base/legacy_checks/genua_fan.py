#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from collections.abc import Iterable
from typing import List

from cmk.base.check_api import LegacyCheckDefinition, saveint
from cmk.base.check_legacy_includes.fan import check_fan
from cmk.base.config import check_info, factory_settings
from cmk.base.plugins.agent_based.agent_based_api.v1 import SNMPTree
from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import StringTable
from cmk.base.plugins.agent_based.utils.genua import DETECT_GENUA

factory_settings["genua_fan_default_levels"] = {
    "lower": (2000, 1000),
    "upper": (8000, 8400),
}


def inventory_genua_fan(string_table: List[StringTable]) -> Iterable[tuple[str, dict[str, object]]]:
    for tree in string_table:
        if not tree:
            continue
        for name, _reading, _state in tree:
            yield name, {}
        return


def check_genua_fan(item, params, info):
    # remove empty elements due to alternative enterprise id in snmp_info
    info = [_f for _f in info if _f]

    map_states = {
        "1": (0, "OK"),
        "2": (1, "warning"),
        "3": (2, "critical"),
        "4": (2, "unknown"),
        "5": (2, "unknown"),
        "6": (2, "unknown"),
    }

    for line in info[0]:
        fanName, fanRPM, fanState = line
        if fanName != item:
            continue

        rpm = saveint(fanRPM)
        state, state_readable = map_states[fanState]
        yield state, "Status: %s" % state_readable
        yield check_fan(rpm, params)


check_info["genua_fan"] = LegacyCheckDefinition(
    detect=DETECT_GENUA,
    discovery_function=inventory_genua_fan,
    check_function=check_genua_fan,
    check_ruleset_name="hw_fans",
    service_name="FAN %s",
    fetch=[
        SNMPTree(
            base=".1.3.6.1.4.1.3717.2.1.1.1.1",
            oids=["2", "3", "4"],
        ),
        SNMPTree(
            base=".1.3.6.1.4.1.3137.2.1.1.1.1",
            oids=["2", "3", "4"],
        ),
    ],
    default_levels_variable="genua_fan_default_levels",
)
