#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from cmk.base.check_api import LegacyCheckDefinition
from cmk.base.check_legacy_includes.elphase import check_elphase
from cmk.base.check_legacy_includes.humidity import check_humidity
from cmk.base.check_legacy_includes.temperature import check_temperature
from cmk.base.config import check_info, factory_settings
from cmk.base.plugins.agent_based.agent_based_api.v1 import SNMPTree
from cmk.base.plugins.agent_based.utils.ra32e import DETECT_RA32E

_SENSOR_TABLES = [
    "1",  # digital-sen1
    "2",  # digital-sen2
    "3",  # digital-sen3
    "4",  # digital-sen4
    "5",  # digital-sen5
    "6",  # digital-sen6
    "7",  # digital-sen7
    "8",  # digital-sen8
]


def parse_ra32e_sensors(info):
    def type_of(sensor):
        def values_until(x):
            return all(sensor[:x]) and not any(sensor[x:])

        if values_until(2):
            return "temp"
        if values_until(3):
            return "temp/active"
        if values_until(4):
            return "temp/analog"
        if values_until(5):
            return "temp/humidity"
        return "unknown"

    parsed: dict[str, dict[str, float | dict]] = {
        "temperature": {},
        "humidity": {},
        "voltage": {},
        "power": {},
    }

    internal, *sensors = info

    for type_, item, value in zip(
        ["temperature", "humidity", "temperature"],
        ["Internal", "Internal", "Heat Index"],
        internal[0],
    ):
        if value:
            parsed[type_][item] = float(value) / 100.0

    for sensor_table, block in zip(_SENSOR_TABLES, sensors):
        for sensor_data in block:
            name = f"Sensor {sensor_table}"
            type_ = type_of(sensor_data)

            # uses the format of elphase.include for power and voltage
            if type_ == "temp":
                temperature, _, _, _, _ = sensor_data
                parsed["temperature"][name] = float(temperature) / 100.0
            elif type_ == "temp/active":
                temperature, _, power_state, _, _ = sensor_data
                parsed["temperature"][name] = float(temperature) / 100.0

                power_status_map = {"1": (0, "power detected"), "0": (2, "no power detected")}
                parsed["power"][name] = {"device_state": power_status_map.get(power_state)}
            elif type_ == "temp/analog":
                temperature, _, voltage, _, _ = sensor_data
                parsed["temperature"][name] = float(temperature) / 100.0
                parsed["voltage"][name] = {"voltage": (int(voltage), None)}
            elif type_ == "temp/humidity":
                temperature, _, humidity, _, heatindex = sensor_data
                parsed["temperature"][name] = float(temperature) / 100.0
                parsed["humidity"][name] = float(humidity) / 100.0
                parsed["temperature"][name.replace("Sensor", "Heat Index")] = (
                    float(heatindex) / 100.0
                )

    return parsed


def inventory_ra32e_sensors(parsed, quantity):
    for name in parsed[quantity]:
        yield name, {}


# .
#   .--Temperature---------------------------------------------------------.
#   |     _____                                   _                        |
#   |    |_   _|__ _ __ ___  _ __   ___ _ __ __ _| |_ _   _ _ __ ___       |
#   |      | |/ _ \ '_ ` _ \| '_ \ / _ \ '__/ _` | __| | | | '__/ _ \      |
#   |      | |  __/ | | | | | |_) |  __/ | | (_| | |_| |_| | | |  __/      |
#   |      |_|\___|_| |_| |_| .__/ \___|_|  \__,_|\__|\__,_|_|  \___|      |
#   |                       |_|                                            |
#   '----------------------------------------------------------------------'

factory_settings["ra32e_temp_defaultlevels"] = {
    "levels": (30.0, 35.0),
}


def check_ra32e_sensors(item, params, parsed):
    temperature = parsed["temperature"].get(item)
    if temperature is None:
        return 3, "no data for sensor"

    unique_name = "ra32e_temp_%s" % item.lower().replace(" ", "")
    return check_temperature(temperature, params, unique_name)


check_info["ra32e_sensors"] = LegacyCheckDefinition(
    detect=DETECT_RA32E,
    parse_function=parse_ra32e_sensors,
    discovery_function=lambda x: inventory_ra32e_sensors(x, "temperature"),
    check_function=check_ra32e_sensors,
    service_name="Temperature %s",
    fetch=[
        SNMPTree(
            base=".1.3.6.1.4.1.20916.1.8.1.1",
            oids=["1.2", "2.1", "4.2"],
        ),
        *(
            SNMPTree(
                base=f".1.3.6.1.4.1.20916.1.8.1.2.{table}",
                oids=[
                    # Note:
                    # The output depends on the kind of sensor and a sensor only outputs relevant values.
                    # The following sensors are mentioned in the MIB from the 13th September 2017:
                    #
                    # sensor            | values
                    # ---------------------------------
                    # Temperature       | 1, 2
                    # Temp/Active Power | 1, 2, 3
                    # Temp/Analog       | 1, 2, 3, 4
                    # Temp/Humidity     | 1, 2, 3, 4, 5
                    #
                    "1",  # digital-sen[1-8]-1 --> Temperature, Temp/Humidity, Temp/Analog, Temp/Active Power: temperature in Celsius
                    "2",  # digital-sen[1-8]-2 --> Temperature, Temp/Humidity, Temp/Analog, Temp/Active Power: temperature in Fahrenheit
                    "3",  # digital-sen[1-8]-3 --> Temp/Humidity: %RH - Temp/Analog: voltage - Temp/Active Power: power state (1=power detected, 0=no power detected)
                    "4",  # digital-sen[1-8]-4 --> Temp/Humidity: heat index Fahrenheit - Temp/Analog: custom reading
                    "5",  # digital-sen[1-8]-5 --> Temp/Humidity: heat index Celsius
                ],
            )
            for table in _SENSOR_TABLES
        ),
    ],
    check_ruleset_name="temperature",
    default_levels_variable="ra32e_temp_defaultlevels",
)

# .
#   .--Humidity------------------------------------------------------------.
#   |              _   _                 _     _ _ _                       |
#   |             | | | |_   _ _ __ ___ (_) __| (_) |_ _   _               |
#   |             | |_| | | | | '_ ` _ \| |/ _` | | __| | | |              |
#   |             |  _  | |_| | | | | | | | (_| | | |_| |_| |              |
#   |             |_| |_|\__,_|_| |_| |_|_|\__,_|_|\__|\__, |              |
#   |                                                  |___/               |
#   '----------------------------------------------------------------------'

factory_settings["ra32e_sensors_humidity_defaultlevels"] = {
    "levels": (70.0, 80.0),
}


def check_ra32e_humidity_sensors(item, params, parsed):
    humidity = parsed["humidity"].get(item)
    if humidity is None:
        return 3, "no data for sensor"

    return check_humidity(humidity, params)


check_info["ra32e_sensors.humidity"] = LegacyCheckDefinition(
    discovery_function=lambda x: inventory_ra32e_sensors(x, "humidity"),
    check_function=check_ra32e_humidity_sensors,
    service_name="Humidity %s",
    check_ruleset_name="humidity",
    default_levels_variable="ra32e_sensors_humidity_defaultlevels",
)

# .
#   .--Voltage-------------------------------------------------------------.
#   |                 __     __    _ _                                     |
#   |                 \ \   / /__ | | |_ __ _  __ _  ___                   |
#   |                  \ \ / / _ \| | __/ _` |/ _` |/ _ \                  |
#   |                   \ V / (_) | | || (_| | (_| |  __/                  |
#   |                    \_/ \___/|_|\__\__,_|\__, |\___|                  |
#   |                                         |___/                        |
#   '----------------------------------------------------------------------'

factory_settings["ra32e_sensors_voltage_defaultlevels"] = {
    "voltage": (210, 180),
}


def check_ra32e_sensors_voltage(item, params, parsed):
    return next(check_elphase(item, params, parsed["voltage"]))


check_info["ra32e_sensors.voltage"] = LegacyCheckDefinition(
    discovery_function=lambda x: inventory_ra32e_sensors(x, "voltage"),
    check_function=check_ra32e_sensors_voltage,
    service_name="Voltage %s",
    check_ruleset_name="ups_outphase",
    default_levels_variable="ra32e_sensors_voltage_defaultlevels",
)

# .
#   .--Power---------------------------------------------------------------.
#   |                     ____                                             |
#   |                    |  _ \ _____      _____ _ __                      |
#   |                    | |_) / _ \ \ /\ / / _ \ '__|                     |
#   |                    |  __/ (_) \ V  V /  __/ |                        |
#   |                    |_|   \___/ \_/\_/ \___|_|                        |
#   |                                                                      |
#   '----------------------------------------------------------------------'


def check_ra32e_power_sensors(item, params, parsed):
    return next(check_elphase(item, params, parsed["power"]))


check_info["ra32e_sensors.power"] = LegacyCheckDefinition(
    discovery_function=lambda x: inventory_ra32e_sensors(x, "power"),
    check_function=check_ra32e_power_sensors,
    service_name="Power State %s",
    check_ruleset_name="ups_outphase",
)
