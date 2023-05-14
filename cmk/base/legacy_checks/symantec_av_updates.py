#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# <<<symantec_av_updates>>>
# 15.05.2015 rev. 1

# <<<symantec_av_updates>>>
# 05/15/2015 rev. 1

# <<<symantec_av_updates>>>
# 09/18/15 rev. 1


import time

from cmk.base.check_api import get_age_human_readable, LegacyCheckDefinition
from cmk.base.config import check_info

symantec_av_updates_default_levels = (259200, 345600)


def inventory_symantec_av_updates(info):
    return [(None, symantec_av_updates_default_levels)]


def check_symantec_av_updates(_no_item, params, info):
    warn, crit = params
    last_text = info[0][0]
    if "/" in last_text:
        if len(last_text) == 10:
            last_broken = time.strptime(last_text, "%m/%d/%Y")
        else:
            last_broken = time.strptime(last_text, "%m/%d/%y")
    else:
        last_broken = time.strptime(last_text, "%d.%m.%Y")

    last_timestamp = time.mktime(last_broken)
    age = time.time() - last_timestamp

    message = "%s since last update" % get_age_human_readable(age)
    if age >= crit:
        return 2, message
    if age >= warn:
        return 1, message
    return 0, message


check_info["symantec_av_updates"] = LegacyCheckDefinition(
    check_function=check_symantec_av_updates,
    check_ruleset_name="antivir_update_age",
    discovery_function=inventory_symantec_av_updates,
    service_name="AV Update Status",
)
