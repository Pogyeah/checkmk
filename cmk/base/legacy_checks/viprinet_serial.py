#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


from cmk.base.check_api import LegacyCheckDefinition
from cmk.base.config import check_info
from cmk.base.plugins.agent_based.agent_based_api.v1 import SNMPTree
from cmk.base.plugins.agent_based.utils.viprinet import DETECT_VIPRINET


def inventory_viprinet_serial(info):
    if info:
        return [(None, None)]
    return []


def check_viprinet_serial(_no_item, _no_params, info):
    return 0, info[0][0]


check_info["viprinet_serial"] = LegacyCheckDefinition(
    detect=DETECT_VIPRINET,
    check_function=check_viprinet_serial,
    discovery_function=inventory_viprinet_serial,
    service_name="Serial Number",
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.35424.1.1",
        oids=["2"],
    ),
)
