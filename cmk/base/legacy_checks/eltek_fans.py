#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# .1.3.6.1.4.1.12148.9.1.17.3.1.1.0 1 --> ELTEK-DISTRIBUTED-MIB::ioUnitID.0
# .1.3.6.1.4.1.12148.9.1.17.3.1.1.1 2 --> ELTEK-DISTRIBUTED-MIB::ioUnitID.1
# .1.3.6.1.4.1.12148.9.1.17.3.1.1.2 3 --> ELTEK-DISTRIBUTED-MIB::ioUnitID.2
# .1.3.6.1.4.1.12148.9.1.17.3.1.1.3 4 --> ELTEK-DISTRIBUTED-MIB::ioUnitID.3
# .1.3.6.1.4.1.12148.9.1.17.3.1.1.4 5 --> ELTEK-DISTRIBUTED-MIB::ioUnitID.4
# .1.3.6.1.4.1.12148.9.1.17.3.1.1.5 6 --> ELTEK-DISTRIBUTED-MIB::ioUnitID.5
# .1.3.6.1.4.1.12148.9.1.17.3.1.1.6 7 --> ELTEK-DISTRIBUTED-MIB::ioUnitID.6
# .1.3.6.1.4.1.12148.9.1.17.3.1.1.7 8 --> ELTEK-DISTRIBUTED-MIB::ioUnitID.7
# .1.3.6.1.4.1.12148.9.1.17.3.1.1.8 9 --> ELTEK-DISTRIBUTED-MIB::ioUnitID.8
# .1.3.6.1.4.1.12148.9.1.17.3.1.1.9 10 --> ELTEK-DISTRIBUTED-MIB::ioUnitID.9
# .1.3.6.1.4.1.12148.9.1.17.3.1.1.10 11 --> ELTEK-DISTRIBUTED-MIB::ioUnitID.10
# .1.3.6.1.4.1.12148.9.1.17.3.1.1.11 12 --> ELTEK-DISTRIBUTED-MIB::ioUnitID.11
# .1.3.6.1.4.1.12148.9.1.17.3.1.1.12 13 --> ELTEK-DISTRIBUTED-MIB::ioUnitID.12
# .1.3.6.1.4.1.12148.9.1.17.3.1.1.13 14 --> ELTEK-DISTRIBUTED-MIB::ioUnitID.13
# .1.3.6.1.4.1.12148.9.1.17.3.1.4.0 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitFanSpeed1.0
# .1.3.6.1.4.1.12148.9.1.17.3.1.4.1 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitFanSpeed1.1
# .1.3.6.1.4.1.12148.9.1.17.3.1.4.2 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitFanSpeed1.2
# .1.3.6.1.4.1.12148.9.1.17.3.1.4.3 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitFanSpeed1.3
# .1.3.6.1.4.1.12148.9.1.17.3.1.4.4 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitFanSpeed1.4
# .1.3.6.1.4.1.12148.9.1.17.3.1.4.5 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitFanSpeed1.5
# .1.3.6.1.4.1.12148.9.1.17.3.1.4.6 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitFanSpeed1.6
# .1.3.6.1.4.1.12148.9.1.17.3.1.4.7 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitFanSpeed1.7
# .1.3.6.1.4.1.12148.9.1.17.3.1.4.8 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitFanSpeed1.8
# .1.3.6.1.4.1.12148.9.1.17.3.1.4.9 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitFanSpeed1.9
# .1.3.6.1.4.1.12148.9.1.17.3.1.4.10 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitFanSpeed1.10
# .1.3.6.1.4.1.12148.9.1.17.3.1.4.11 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitFanSpeed1.11
# .1.3.6.1.4.1.12148.9.1.17.3.1.4.12 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitFanSpeed1.12
# .1.3.6.1.4.1.12148.9.1.17.3.1.4.13 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitFanSpeed1.13
# .1.3.6.1.4.1.12148.9.1.17.3.1.6.0 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitFanSpeed2.0
# .1.3.6.1.4.1.12148.9.1.17.3.1.6.1 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitFanSpeed2.1
# .1.3.6.1.4.1.12148.9.1.17.3.1.6.2 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitFanSpeed2.2
# .1.3.6.1.4.1.12148.9.1.17.3.1.6.3 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitFanSpeed2.3
# .1.3.6.1.4.1.12148.9.1.17.3.1.6.4 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitFanSpeed2.4
# .1.3.6.1.4.1.12148.9.1.17.3.1.6.5 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitFanSpeed2.5
# .1.3.6.1.4.1.12148.9.1.17.3.1.6.6 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitFanSpeed2.6
# .1.3.6.1.4.1.12148.9.1.17.3.1.6.7 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitFanSpeed2.7
# .1.3.6.1.4.1.12148.9.1.17.3.1.6.8 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitFanSpeed2.8
# .1.3.6.1.4.1.12148.9.1.17.3.1.6.9 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitFanSpeed2.9
# .1.3.6.1.4.1.12148.9.1.17.3.1.6.10 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitFanSpeed2.10
# .1.3.6.1.4.1.12148.9.1.17.3.1.6.11 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitFanSpeed2.11
# .1.3.6.1.4.1.12148.9.1.17.3.1.6.12 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitFanSpeed2.12
# .1.3.6.1.4.1.12148.9.1.17.3.1.6.13 0 --> ELTEK-DISTRIBUTED-MIB::ioUnitFanSpeed2.13

# suggested by customer

# mypy: disable-error-code="var-annotated"

from cmk.base.check_api import LegacyCheckDefinition
from cmk.base.config import check_info, factory_settings
from cmk.base.plugins.agent_based.agent_based_api.v1 import SNMPTree
from cmk.base.plugins.agent_based.utils.eltek import DETECT_ELTEK

factory_settings["eltek_fans_default_variables"] = {
    "levels": (99, 100),
}


def inventory_eltek_fans(info):
    inventory = []
    for index, fan1, fan2 in info:
        if fan1 and int(fan1) > 0:
            inventory.append(("1/%s" % index, {}))
        if fan2 and int(fan2) > 0:
            inventory.append(("2/%s" % index, {}))
    return inventory


def check_eltek_fans(item, params, info):
    for index, fan1, fan2 in info:
        for fan_id, reading in [("1", float(fan1)), ("2", float(fan2))]:
            if "%s/%s" % (fan_id, index) == item:
                state = 0
                infotext = "%.1f%% of max RPM" % reading
                levelstext = "at"
                warn, crit = params["levels"]
                if reading >= crit:
                    state = 2
                elif reading >= warn:
                    state = 1

                if params.get("levels_lower", ""):
                    if reading < crit:
                        state = 2
                        levelstext = "below"
                    elif reading < warn:
                        state = 1
                        levelstext = "below"

                if state > 0:
                    infotext += " (warn/crit %s %.1f%%/%.1f%%)" % (levelstext, warn, crit)

                return state, infotext
    return None


check_info["eltek_fans"] = LegacyCheckDefinition(
    detect=DETECT_ELTEK,
    discovery_function=inventory_eltek_fans,
    check_function=check_eltek_fans,
    service_name="Fan %s",
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.12148.9.1.17.3.1",
        oids=["1", "4", "6"],
    ),
    default_levels_variable="eltek_fans_default_variables",
    check_ruleset_name="hw_fans_perc",
)
