#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# Example for info:

# [['0'], ['1'], ['2'], ['3'], ['4'], ['5'], ['Critical'], ['Critical'],
# ['Warning'], ['Warning'], ['Warning'], ['Multiple fan failures'],
# ['Power Supply 1 AC Power Removed'], ['System Running Nonredundant Power'],
# ['Fan 7 Failure'], ['Fan 8 Failure']]

#   critical(0),
#   nonCritical(2),
#   systemLevel(4),
#   normal(255)


from cmk.base.check_api import contains, LegacyCheckDefinition
from cmk.base.config import check_info
from cmk.base.plugins.agent_based.agent_based_api.v1 import SNMPTree


def inventory_ibm_rsa_health(info):
    if len(info) > 0:
        return [(None, None)]
    return []


def check_ibm_rsa_health(_no_item, _no_params, info):
    num_alerts = int((len(info) - 1) / 3)
    infotext = ""
    for i in range(0, num_alerts):
        state = info[num_alerts + 1 + i][0]
        text = info[num_alerts * 2 + 1 + i][0]
        if infotext != "":
            infotext += ", "
        infotext += "%s(%s)" % (text, state)

    state = info[0][0]
    if state == "255":
        return 0, "no problem found"
    if state in ["0", "2"]:
        return 2, infotext
    if state == "4":
        return 1, infotext
    return 3, infotext


check_info["ibm_rsa_health"] = LegacyCheckDefinition(
    detect=contains(".1.3.6.1.2.1.1.1.0", "Remote Supervisor Adapter"),
    check_function=check_ibm_rsa_health,
    discovery_function=inventory_ibm_rsa_health,
    service_name="System health",
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.2.3.51.1.2",
        oids=["7"],
    ),
)
