#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


from cmk.base.check_api import any_of, contains, LegacyCheckDefinition, saveint
from cmk.base.config import check_info
from cmk.base.plugins.agent_based.agent_based_api.v1 import SNMPTree


def inventory_blade_powerfan(info):
    return [(line[0], (50, 40)) for line in info if line[0] != "" and line[1] == "1"]


def check_blade_powerfan(item, params, info):
    warn_perc, crit_perc = params
    for index, present, status, _fancount, speedperc, rpm, ctrlstate in info:
        if index != item:
            continue
        perfdata = [("perc", speedperc, warn_perc, crit_perc, "0", "100"), ("rpm", rpm)]
        speedperc_int = saveint(speedperc)
        if present != "1":
            return (2, "Fan not present", perfdata)
        if status != "1":
            return (2, "Status not OK", perfdata)
        if ctrlstate != "0":
            return (2, "Controller state not OK", perfdata)
        if speedperc_int <= crit_perc:
            return (2, "Speed at %d%% of max (crit at %d%%)" % (speedperc_int, crit_perc), perfdata)
        if speedperc_int <= warn_perc:
            return (
                1,
                "Speed at %d%% of max (warning at %d%%)" % (speedperc_int, warn_perc),
                perfdata,
            )
        return (0, "Speed at %s RPM (%d%% of max)" % (rpm, speedperc_int), perfdata)

    return (3, "Device %s not found in SNMP data" % item)


check_info["blade_powerfan"] = LegacyCheckDefinition(
    detect=any_of(
        contains(".1.3.6.1.2.1.1.1.0", "BladeCenter Management Module"),
        contains(".1.3.6.1.2.1.1.1.0", "BladeCenter Advanced Management Module"),
    ),
    check_function=check_blade_powerfan,
    discovery_function=inventory_blade_powerfan,
    service_name="Power Module Cooling Device %s",
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.2.3.51.2.2.6.1.1",
        oids=["1", "2", "3", "4", "5", "6", "7"],
    ),
)
