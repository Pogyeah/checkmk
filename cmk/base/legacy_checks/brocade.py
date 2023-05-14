#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


from cmk.base.check_api import any_of, equals, LegacyCheckDefinition, saveint, startswith
from cmk.base.check_legacy_includes.fan import check_fan
from cmk.base.check_legacy_includes.temperature import check_temperature
from cmk.base.config import check_info, factory_settings
from cmk.base.plugins.agent_based.agent_based_api.v1 import SNMPTree

# Example output from agent:
# [['1', '24', 'SLOT #0: TEMP #1'],
# ['2', '12', 'SLOT #0: TEMP #2'],
# ['3', '12', 'SLOT #0: TEMP #3'],
# ['4', '4687', 'FAN #1'],
# ['5', '4560', 'FAN #2'],
# ['6', '4821', 'FAN #3'],
# ['7', '1', 'Power Supply #1'],
# ['8', '1', 'Power Supply #2']]


def brocade_sensor_convert(info, what):
    return_list = []
    for presence, state, name in info:
        name = name.lstrip()  # remove leading spaces provided via SNMP
        if name.startswith(what) and presence != "6" and (saveint(state) > 0 or what == "Power"):
            sensor_id = name.split("#")[-1]
            return_list.append([sensor_id, name, state])
    return return_list


brocade_fan_default_levels = {"lower": (3000, 2800)}


def inventory_brocade_fan(info):
    converted = brocade_sensor_convert(info, "FAN")
    return [(x[0], brocade_fan_default_levels) for x in converted]


def check_brocade_fan(item, params, info):
    converted = brocade_sensor_convert(info, "FAN")
    if isinstance(params, tuple):  # old format
        params = {"lower": params}

    for snmp_item, _name, value in converted:
        if item == snmp_item:
            return check_fan(int(value), params)
    return None


check_info["brocade.fan"] = LegacyCheckDefinition(
    detect=any_of(
        startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.1588.2.1.1"),
        startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.24.1.1588.2.1.1"),
        startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.1588.2.2.1"),
        startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.1588.3.3.1"),
        equals(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.1916.2.306"),
    ),
    check_function=check_brocade_fan,
    discovery_function=inventory_brocade_fan,
    service_name="FAN %s",
    check_ruleset_name="hw_fans",
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.1588.2.1.1.1.1.22.1",
        oids=["3", "4", "5"],
    ),
)


def inventory_brocade_power(info):
    converted = brocade_sensor_convert(info, "Power")
    return [(x[0], None) for x in converted]


def check_brocade_power(item, _no_params, info):
    converted = brocade_sensor_convert(info, "Power")
    for snmp_item, name, value in converted:
        if item == snmp_item:
            value = int(value)
            if value != 1:
                return 2, "Error on supply %s" % name
            return 0, "No problems found"

    return 3, "Supply not found"


check_info["brocade.power"] = LegacyCheckDefinition(
    detect=any_of(
        startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.1588.2.1.1"),
        startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.24.1.1588.2.1.1"),
        startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.1588.2.2.1"),
        startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.1588.3.3.1"),
        equals(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.1916.2.306"),
    ),
    check_function=check_brocade_power,
    discovery_function=inventory_brocade_power,
    service_name="Power supply %s",
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.1588.2.1.1.1.1.22.1",
        oids=["3", "4", "5"],
    ),
)

factory_settings["brocade_temp_default_levels"] = {"levels": (55.0, 60.0)}


def inventory_brocade_temp(info):
    converted = brocade_sensor_convert(info, "SLOT")
    return [(x[0], {}) for x in converted]


def check_brocade_temp(item, params, info):
    converted = brocade_sensor_convert(info, "SLOT")
    for snmp_item, _name, value in converted:
        if item == snmp_item:
            return check_temperature(int(value), params, "brocade_temp_%s" % item)
    return None


check_info["brocade.temp"] = LegacyCheckDefinition(
    detect=any_of(
        startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.1588.2.1.1"),
        startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.24.1.1588.2.1.1"),
        startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.1588.2.2.1"),
        startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.1588.3.3.1"),
        equals(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.1916.2.306"),
    ),
    check_function=check_brocade_temp,
    discovery_function=inventory_brocade_temp,
    service_name="Temperature Ambient %s",
    check_ruleset_name="temperature",
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.1588.2.1.1.1.1.22.1",
        oids=["3", "4", "5"],
    ),
    default_levels_variable="brocade_temp_default_levels",
)
