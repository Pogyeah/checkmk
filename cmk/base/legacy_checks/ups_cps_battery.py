#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from cmk.base.check_api import LegacyCheckDefinition
from cmk.base.check_legacy_includes.temperature import check_temperature
from cmk.base.config import check_info, factory_settings
from cmk.base.plugins.agent_based.agent_based_api.v1 import SNMPTree
from cmk.base.plugins.agent_based.utils.ups import DETECT_UPS_CPS


def parse_ups_cps_battery(info):
    parsed: dict[str, float] = {}

    if info[0][0]:
        parsed["capacity"] = int(info[0][0])

    # The MIB explicitly declares this to be Celsius
    if info[0][1] and info[0][1] != "NULL":
        parsed["temperature"] = int(info[0][1])

    # A TimeTick is 1/100 s
    if info[0][2]:
        parsed["battime"] = float(info[0][2]) / 100.0
    return parsed


# .
#   .--Temperature---------------------------------------------------------.
#   |     _____                                   _                        |
#   |    |_   _|__ _ __ ___  _ __   ___ _ __ __ _| |_ _   _ _ __ ___       |
#   |      | |/ _ \ '_ ` _ \| '_ \ / _ \ '__/ _` | __| | | | '__/ _ \      |
#   |      | |  __/ | | | | | |_) |  __/ | | (_| | |_| |_| | | |  __/      |
#   |      |_|\___|_| |_| |_| .__/ \___|_|  \__,_|\__|\__,_|_|  \___|      |
#   |                       |_|                                            |
#   '----------------------------------------------------------------------'


def inventory_ups_cps_battery_temp(parsed):
    if "temperature" in parsed:
        yield "Battery", {}


def check_ups_cps_battery_temp(item, params, parsed):
    if "temperature" in parsed:
        return check_temperature(parsed["temperature"], params, "ups_cps_battery_temp")
    return None


check_info["ups_cps_battery.temp"] = LegacyCheckDefinition(
    discovery_function=inventory_ups_cps_battery_temp,
    check_function=check_ups_cps_battery_temp,
    service_name="Temperature %s",
    check_ruleset_name="temperature",
)

# .
#   .--Capacity------------------------------------------------------------.
#   |                ____                       _ _                        |
#   |               / ___|__ _ _ __   __ _  ___(_) |_ _   _                |
#   |              | |   / _` | '_ \ / _` |/ __| | __| | | |               |
#   |              | |__| (_| | |_) | (_| | (__| | |_| |_| |               |
#   |               \____\__,_| .__/ \__,_|\___|_|\__|\__, |               |
#   |                         |_|                     |___/                |
#   '----------------------------------------------------------------------'

factory_settings["ups_cps_battery"] = {
    "capacity": (95, 90),
}


def inventory_ups_cps_battery(parsed):
    if "capacity" in parsed:
        yield None, {}


def check_ups_cps_battery(item, params, parsed):
    def check_lower_levels(value, levels):
        if not levels:
            return 0
        warn, crit = levels
        if value < crit:
            return 2
        if value < warn:
            return 1
        return 0

    capacity = parsed["capacity"]
    capacity_params = params["capacity"]
    capacity_status = check_lower_levels(capacity, capacity_params)
    if capacity_status:
        levelstext = " (warn/crit at %d/%d%%)" % capacity_params
    else:
        levelstext = ""
    yield capacity_status, ("Capacity at %d%%" % capacity) + levelstext

    battime = parsed["battime"]
    # WATO rule stores remaining time in minutes
    battime_params = params.get("battime")
    battime_status = check_lower_levels(battime / 60.0, battime_params)
    if battime_status:
        levelstext = " (warn/crit at %d/%d min)" % battime_params
    else:
        levelstext = ""
    yield battime_status, ("%.0f minutes remaining on battery" % (battime / 60.0)) + levelstext


check_info["ups_cps_battery"] = LegacyCheckDefinition(
    detect=DETECT_UPS_CPS,
    parse_function=parse_ups_cps_battery,
    default_levels_variable="ups_cps_battery",
    discovery_function=inventory_ups_cps_battery,
    check_function=check_ups_cps_battery,
    service_name="UPS Battery",
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.3808.1.1.1.2.2",
        oids=["1", "3", "4"],
    ),
    check_ruleset_name="ups_capacity",
)
