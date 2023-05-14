#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


from cmk.base.check_api import LegacyCheckDefinition, saveint
from cmk.base.config import check_info, factory_settings

factory_settings["qmail_stats_default_levels"] = {
    "deferred": (10, 20),
}


def inventory_qmail_stats(info):
    if len(info) > 0:
        return [("", {})]
    return []


def check_qmail_stats(_no_item, params, info):
    if not isinstance(params, dict):
        params = {
            "deferred": params,
        }
    warn, crit = params["deferred"]
    queue_length = saveint(info[0][-1])
    state = 0
    label = ""
    if queue_length >= crit:
        state = 2
    elif queue_length >= warn:
        state = 1
    if state:
        label = "(Levels at %d/%d)" % (warn, crit)

    perf = [("queue", queue_length, warn, crit)]
    message = "Mailqueue length is %d %s" % (queue_length, label)
    return state, message, perf


check_info["qmail_stats"] = LegacyCheckDefinition(
    discovery_function=inventory_qmail_stats,
    check_function=check_qmail_stats,
    service_name="Qmail Queue %s",
    default_levels_variable="qmail_stats_default_levels",
    check_ruleset_name="mail_queue_length",
)
