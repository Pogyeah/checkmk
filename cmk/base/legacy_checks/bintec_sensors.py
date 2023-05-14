#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


# mypy: disable-error-code="var-annotated"

from cmk.base.check_api import LegacyCheckDefinition, startswith
from cmk.base.check_legacy_includes.fan import check_fan
from cmk.base.check_legacy_includes.temperature import check_temperature
from cmk.base.config import check_info, factory_settings
from cmk.base.plugins.agent_based.agent_based_api.v1 import SNMPTree

#   .--fans----------------------------------------------------------------.
#   |                          __                                          |
#   |                         / _| __ _ _ __  ___                          |
#   |                        | |_ / _` | '_ \/ __|                         |
#   |                        |  _| (_| | | | \__ \                         |
#   |                        |_|  \__,_|_| |_|___/                         |
#   |                                                                      |
#   '----------------------------------------------------------------------'

factory_settings["bintec_sensors_fan_default_levels"] = {
    "lower": (2000, 1000),
}


def inventory_bintec_sensors_fan(info):
    inventory = []
    for _sensor_id, sensor_descr, sensor_type, _sensor_value, _sensor_unit in info:
        if sensor_type == "2":
            inventory.append((sensor_descr, {}))
    return inventory


def check_bintec_sensors_fan(item, params, info):
    for _sensor_id, sensor_descr, _sensor_type, sensor_value, _sensor_unit in info:
        if sensor_descr == item:
            return check_fan(int(sensor_value), params)
    return None


check_info["bintec_sensors.fan"] = LegacyCheckDefinition(
    detect=startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.272.4"),
    check_function=check_bintec_sensors_fan,
    discovery_function=inventory_bintec_sensors_fan,
    service_name="%s",
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.272.4.17.7.1.1.1",
        oids=["2", "3", "4", "5", "7"],
    ),
    default_levels_variable="bintec_sensors_fan_default_levels",
    check_ruleset_name="hw_fans",
)

# .
#   .--temp----------------------------------------------------------------.
#   |                       _                                              |
#   |                      | |_ ___ _ __ ___  _ __                         |
#   |                      | __/ _ \ '_ ` _ \| '_ \                        |
#   |                      | ||  __/ | | | | | |_) |                       |
#   |                       \__\___|_| |_| |_| .__/                        |
#   |                                        |_|                           |
#   '----------------------------------------------------------------------'

factory_settings["bintec_sensors_temp_default_levels"] = {"levels": (35.0, 40.0)}


def inventory_bintec_sensors_temp(info):
    for _sensor_id, sensor_descr, sensor_type, _sensor_value, _sensor_unit in info:
        if sensor_type == "1":
            yield sensor_descr, {}


def check_bintec_sensors_temp(item, params, info):
    for _sensor_id, sensor_descr, _sensor_type, sensor_value, _sensor_unit in info:
        if sensor_descr == item:
            return check_temperature(int(sensor_value), params, "bintec_sensors_%s" % item)

    return 3, "Sensor not found in SNMP data"


check_info["bintec_sensors.temp"] = LegacyCheckDefinition(
    detect=startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.272.4"),
    check_function=check_bintec_sensors_temp,
    discovery_function=inventory_bintec_sensors_temp,
    service_name="Temperature %s",
    check_ruleset_name="temperature",
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.272.4.17.7.1.1.1",
        oids=["2", "3", "4", "5", "7"],
    ),
    default_levels_variable="bintec_sensors_temp_default_levels",
)

# .
#   .--voltage-------------------------------------------------------------.
#   |                             _ _                                      |
#   |                 __   _____ | | |_ __ _  __ _  ___                    |
#   |                 \ \ / / _ \| | __/ _` |/ _` |/ _ \                   |
#   |                  \ V / (_) | | || (_| | (_| |  __/                   |
#   |                   \_/ \___/|_|\__\__,_|\__, |\___|                   |
#   |                                        |___/                         |
#   '----------------------------------------------------------------------'


def inventory_bintec_sensors_voltage(info):
    inventory = []
    for _sensor_id, sensor_descr, sensor_type, _sensor_value, _sensor_unit in info:
        if sensor_type == "3":
            inventory.append((sensor_descr, None))
    return inventory


def check_bintec_sensors_voltage(item, _no_params, info):
    for _sensor_id, sensor_descr, _sensor_type, sensor_value, _sensor_unit in info:
        if sensor_descr == item:
            sensor_value = int(sensor_value) / 1000.0

            message = "%s is at %s V" % (sensor_descr, sensor_value)
            perfdata = [("voltage", str(sensor_value) + "V")]

            return 0, message, perfdata

    return 3, "Sensor %s not found" % item


check_info["bintec_sensors.voltage"] = LegacyCheckDefinition(
    detect=startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.272.4"),
    check_function=check_bintec_sensors_voltage,
    discovery_function=inventory_bintec_sensors_voltage,
    service_name="Voltage %s",
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.272.4.17.7.1.1.1",
        oids=["2", "3", "4", "5", "7"],
    ),
)

# .
