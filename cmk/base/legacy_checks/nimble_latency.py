#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


# mypy: disable-error-code="var-annotated,arg-type,index"

import collections

from cmk.base.check_api import (
    check_levels,
    get_parsed_item_data,
    get_percent_human_readable,
    LegacyCheckDefinition,
    startswith,
)
from cmk.base.config import check_info, factory_settings
from cmk.base.plugins.agent_based.agent_based_api.v1 import SNMPTree

# Default levels: issue a WARN/CRIT if 1%/2% of read or write IO
# operations have a latency of 10-20 ms or above.
factory_settings["nimble_latency_default_levels"] = {
    # The latency range that is used to start measuring against levels.
    # The numbers of operations of and above this range are added and then
    # taken as a percentage of the total number of operations.
    "range_reference": "20",
    # These are percentage values!
    "read": (10.0, 20.0),
    "write": (10.0, 20.0),
}

NimbleReadsType = "read"
NimbleWritesType = "write"


def parse_nimble_read_latency(info):
    range_keys = [
        ("total", "Total"),
        ("0.1", "0-0.1 ms"),
        ("0.2", "0.1-0.2 ms"),
        ("0.5", "0.2-0.5 ms"),
        ("1", "0.5-1.0 ms"),
        ("2", "1-2 ms"),
        ("5", "2-5 ms"),
        ("10", "5-10 ms"),
        ("20", "10-20 ms"),
        ("50", "20-50 ms"),
        ("100", "50-100 ms"),
        ("200", "100-200 ms"),
        ("500", "200-500 ms"),
        ("1000", "500+ ms"),
    ]
    parsed = {}

    for line in info:
        vol_name = line[0]
        for ty, start_idx in [
            (NimbleReadsType, 1),
            (NimbleWritesType, 15),
        ]:
            values = line[start_idx : start_idx + 14]
            latencies = {}
            for (key, title), value_str in zip(range_keys, values):
                try:
                    value = int(value_str)
                except ValueError:
                    continue
                if key == "total":
                    latencies[key] = value
                    continue
                # maintain the key order so that long output is sorted later
                latencies.setdefault("ranges", collections.OrderedDict())[key] = title, value
            parsed.setdefault(vol_name, {}).setdefault(ty, latencies)

    return parsed


def inventory_nimble_latency(parsed, ty):
    for vol_name, vol_attrs in parsed.items():
        if vol_attrs[ty]:
            yield vol_name, {}


def _check_nimble_latency(item, params, data, ty):
    ty_data = data.get(ty)
    if ty_data is None:
        return

    total_value = ty_data["total"]
    if total_value == 0:
        yield 0, "No current %s operations" % ty
        return

    range_reference = float(params["range_reference"])
    running_total_percent = 0
    results = []
    for key, (title, value) in ty_data["ranges"].items():
        metric_name = "nimble_%s_latency_%s" % (ty, key.replace(".", ""))
        percent_value = value / total_value * 100

        if float(key) >= range_reference:
            running_total_percent += percent_value

        results.append(
            check_levels(
                value=percent_value,
                dsname=metric_name,
                params=None,
                human_readable_func=get_percent_human_readable,
                infoname=title,
            )
        )

    yield check_levels(
        value=running_total_percent,
        dsname=None,
        params=params[ty],
        human_readable_func=get_percent_human_readable,
        infoname="At or above %s" % ty_data["ranges"][params["range_reference"]][0],
    )

    yield 0, "\nLatency breakdown:"
    for _state, infotext, perfdata in results:
        yield 0, infotext, perfdata


@get_parsed_item_data
def check_nimble_latency_reads(item, params, data):
    return _check_nimble_latency(item, params, data, NimbleReadsType)


check_info["nimble_latency"] = LegacyCheckDefinition(
    detect=startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.37447.3.1"),
    parse_function=parse_nimble_read_latency,
    discovery_function=lambda parsed: inventory_nimble_latency(parsed, NimbleReadsType),
    check_function=check_nimble_latency_reads,
    service_name="Volume %s Read IO",
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.37447.1.2.1",
        oids=[
            "3",
            "13",
            "21",
            "22",
            "23",
            "24",
            "25",
            "26",
            "27",
            "28",
            "29",
            "30",
            "31",
            "32",
            "33",
            "34",
            "39",
            "40",
            "41",
            "42",
            "43",
            "44",
            "45",
            "46",
            "47",
            "48",
            "49",
            "50",
            "51",
        ],
    ),
    check_ruleset_name="nimble_latency",
    default_levels_variable="nimble_latency_default_levels",
)


@get_parsed_item_data
def check_nimble_latency_writes(item, params, data):
    return _check_nimble_latency(item, params, data, NimbleWritesType)


check_info["nimble_latency.write"] = LegacyCheckDefinition(
    discovery_function=lambda parsed: inventory_nimble_latency(parsed, NimbleWritesType),
    check_function=check_nimble_latency_writes,
    service_name="Volume %s Write IO",
    check_ruleset_name="nimble_latency",
    default_levels_variable="nimble_latency_default_levels",
)
