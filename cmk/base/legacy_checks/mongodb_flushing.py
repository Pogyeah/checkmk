#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# <<<mongodb_flushing>>>
# average_ms 1.28893335892
# last_ms 0
# flushed 36479


import time

from cmk.base.check_api import (
    check_levels,
    get_age_human_readable,
    get_average,
    LegacyCheckDefinition,
)
from cmk.base.config import check_info


def inventory_mongodb_flushing(info):
    # This check has no default parameters
    # The average/last flush time highly depends on the size of the mongodb setup
    return [(None, {})]


def check_mongodb_flushing(_no_item, params, info):
    info_dict = dict(info)

    if not {"last_ms", "average_ms", "flushed"} <= set(info_dict):  # check if keys in dict
        yield 3, "missing data: %s" % (
            _get_missing_keys(["last_ms", "average_ms", "flushed"], info_dict)
        )
        return

    try:
        last_ms = float(info_dict["last_ms"])
        avg_flush_time = float(info_dict["average_ms"]) / 1000.0
        flushed = int(info_dict["flushed"])
    except (ValueError, TypeError):
        yield 3, "Invalid data: last_ms: %s, average_ms: %s, flushed:%s" % (
            info_dict["last_ms"],
            info_dict["average_ms"],
            info_dict["flushed"],
        )
        return

    if "average_time" in params:
        warn, crit, avg_interval = params["average_time"]
        avg_ms_compute = get_average("flushes", time.time(), last_ms, avg_interval)
        yield check_levels(
            avg_ms_compute,
            None,
            (warn, crit),
            unit="ms",
            infoname="Average flush time over %s minutes" % (avg_interval),
        )

    yield check_levels(
        (last_ms / 1000.0),
        "flush_time",
        params.get("last_time"),
        unit="s",
        infoname="Last flush time",
    )

    yield 0, "Flushes since restart: %s" % flushed, [("flushed", flushed)]
    yield 0, "Average flush time since restart: %s" % get_age_human_readable(avg_flush_time), [
        ("avg_flush_time", avg_flush_time)
    ]


def _get_missing_keys(key_list, info_dict):
    missing_keys = []
    for key in key_list:
        if key not in info_dict:
            missing_keys += [str(key)]
    return " and ".join(sorted(missing_keys))


check_info["mongodb_flushing"] = LegacyCheckDefinition(
    discovery_function=inventory_mongodb_flushing,
    check_function=check_mongodb_flushing,
    service_name="MongoDB Flushing",
    check_ruleset_name="mongodb_flushing",
)
