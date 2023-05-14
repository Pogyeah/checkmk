#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


# mypy: disable-error-code="var-annotated,assignment"

import collections

from cmk.base.check_api import discover, get_parsed_item_data, LegacyCheckDefinition
from cmk.base.check_legacy_includes.df import df_check_filesystem_single, FILESYSTEM_DEFAULT_PARAMS
from cmk.base.config import check_info, factory_settings

# example output
# <<<aix_paging>>>
# Page Space      Physical Volume   Volume Group    Size %Used   Active    Auto    Type   Chksum
# hd6                   hdisk11                rootvg       10240MB    23        yes        yes       lv       0

factory_settings["filesystem_default_levels"] = FILESYSTEM_DEFAULT_PARAMS


AIXPaging = collections.namedtuple(  # pylint: disable=collections-namedtuple-call
    "AIXPaging", ["group", "size_mb", "usage_perc", "active", "auto", "type"]
)


def parse_aix_paging(info):
    map_type = {
        "lv": "logical volume",
        "nfs": "NFS",
    }

    parsed = {}
    if len(info) <= 1:
        return parsed

    # First line is the header
    for line in info[1:]:
        try:
            # Always given in MB, eg. 1234MB
            size = int(line[3][:-2])
        except ValueError:
            continue
        try:
            usage = int(line[4])
        except ValueError:
            continue
        paging_type = map_type.get(line[7], "unknown[%s]" % line[7])
        parsed.setdefault(
            "%s/%s" % (line[0], line[1]),
            AIXPaging(line[2], size, usage, line[5], line[6], paging_type),
        )
    return parsed


@get_parsed_item_data
def check_aix_paging(item, params, data):
    avail_mb = data.size_mb * (1 - data.usage_perc / 100.0)
    yield df_check_filesystem_single(item, data.size_mb, avail_mb, 0, None, None, params)
    yield 0, "Active: %s, Auto: %s, Type: %s" % (data.active, data.auto, data.type)


check_info["aix_paging"] = LegacyCheckDefinition(
    parse_function=parse_aix_paging,
    discovery_function=discover(),
    check_function=check_aix_paging,
    service_name="Page Space %s",
    check_ruleset_name="filesystem",
    default_levels_variable="filesystem_default_levels",
)
