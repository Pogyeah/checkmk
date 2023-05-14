#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# <<<netapp_api_info:sep(9)>>>
# build-timestamp 1425927992
# is-clustered    true
# version NetApp Release 8.3: Mon Mar 09 19:06:32 PDT 2015
# clu1-01 board-speed 2933
# clu1-01 board-type  NetApp VSim
# clu1-01 cpu-microcode-version   21
# clu1-01 cpu-processor-id    0x206c2
# clu1-01 cpu-serial-number   999999
# clu1-01 memory-size 8192
# clu1-01 number-of-processors    2
# clu1-01 prod-type   FAS


from cmk.base.check_api import LegacyCheckDefinition
from cmk.base.config import check_info


def inventory_netapp_api_info(info):
    return [(None, None)]


def check_netapp_api_info(item, _no_params, info):
    for line in info:
        if line[0] == "version":
            return 0, "Version: %s" % line[1]
    return None


check_info["netapp_api_info"] = LegacyCheckDefinition(
    check_function=check_netapp_api_info,
    discovery_function=inventory_netapp_api_info,
    service_name="NetApp Version",
)
