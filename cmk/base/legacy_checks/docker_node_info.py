#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


from cmk.base.check_api import check_levels, discover_single, LegacyCheckDefinition
from cmk.base.config import check_info


def discover_docker_node_info(info):
    if info:
        yield None, {}


def check_docker_node_info(_no_item, _no_params, parsed):
    if "Name" in parsed:
        yield 0, "Daemon running on host %s" % parsed["Name"]
    for state, key in enumerate(("Warning", "Critical", "Unknown"), 1):
        if key in parsed:
            yield state, parsed[key]


check_info["docker_node_info"] = LegacyCheckDefinition(
    # section is already migrated!
    discovery_function=discover_docker_node_info,
    check_function=check_docker_node_info,
    service_name="Docker node info",
)


def check_docker_node_containers(_no_item, params, parsed):
    for title, key, levels_prefix in (
        ("containers", "Containers", ""),
        ("running", "ContainersRunning", "running_"),
        ("paused", "ContainersPaused", "paused_"),
        ("stopped", "ContainersStopped", "stopped_"),
    ):
        count = parsed.get(key)
        if count is None:
            yield 3, "%s: count not present in agent output" % title.title()
            continue

        levels = params.get("%supper_levels" % levels_prefix, (None, None))
        levels_lower = params.get("%slower_levels" % levels_prefix, (None, None))
        yield check_levels(
            count,
            title,
            levels + levels_lower,
            human_readable_func=lambda x: "%d" % x,
            infoname=title.title(),
        )


check_info["docker_node_info.containers"] = LegacyCheckDefinition(
    # section is already migrated!
    discovery_function=discover_single,
    check_function=check_docker_node_containers,
    service_name="Docker containers",
    check_ruleset_name="docker_node_containers",
)
