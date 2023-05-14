#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# Example output from agent:
# <<<hyperv_vms>>>
# DMZ-DC1                         Running 4.21:44:58          Operating normally
# DMZ-DC2                         Running 4.21:44:47          Operating normally

# Another example, here with a snapshow with spaces in the name:
# <<<hyperv_vms>>>
# windows-hyperv2-z4058044                              Running 21:33:08   Operating normally
# windows-hyperv2-z4058044_snap (23.05.2014 - 09:29:29) Running 18:20:34   Operating normally
# windows-hyperv2-z4065002                              Running 11:04:50   Operating normally
# windows-hyperv2-z4065084                              Running 1.10:42:33 Operating normally
# windows-hyperv2-z4133235                              Running 1.03:52:18 Operating normally

# A broken version of the agent outputted this:
# <<<hyperv_vms>>>
# z4058044                        Running 21:19:14            Operating normally
# z4058044_snap (2...             Running 18:06:39            Operating normally
# z4065002                        Running 10:50:55            Operating normally
# z4065084                        Running 1.10:28:39          Operating normally
# z4133235                        Running 1.03:38:23          Operating normally

# A Version with a plugin that uses tab as seperator and quotes the strings:
# <<<hyperv_vms:sep(9)>>>
# "Name"  "State" "Uptime"        "Status"
# "z4058013"      "Running"       "06:05:16"      "Operating normally"
# "z4058020"      "Running"       "01:01:57"      "Operating normally"
# "z4058021"      "Running"       "01:02:11"      "Operating normally"
# "z4065012"      "Running"       "01:02:04"      "Operating normally"
# "z4065013"      "Running"       "07:47:27"      "Operating normally"
# "z4065020"      "Running"       "01:02:09"      "Operating normally"
# "z4065025"      "Running"       "01:02:05"      "Operating normally"
# "z4133199"      "Running"       "00:57:23"      "Operating normally"

# result:
# {
#   "windows-hyperv2-z4058044_snap (23.05.2014 - 09:29:29)" : {
#        "vm_state" : "Running",
#        "uptime" : "1.10:42:33",
#        "state_msg" : "Operating normally",
#    }
# }

# these default values were suggested by Aldi Sued


from cmk.base.check_api import get_parsed_item_data, LegacyCheckDefinition
from cmk.base.config import check_info, factory_settings

factory_settings["hyperv_vms_default_levels"] = {
    "FastSaved": 0,
    "FastSavedCritical": 2,
    "FastSaving": 0,
    "FastSavingCritical": 2,
    "Off": 1,
    "OffCritical": 2,
    "Other": 3,
    "Paused": 0,
    "PausedCritical": 2,
    "Pausing": 0,
    "PausingCritical": 2,
    "Reset": 1,
    "ResetCritical": 2,
    "Resuming": 0,
    "ResumingCritical": 2,
    "Running": 0,
    "RunningCritical": 2,
    "Saved": 0,
    "SavedCritical": 2,
    "Saving": 0,
    "SavingCritical": 2,
    "Starting": 0,
    "StartingCritical": 2,
    "Stopping": 1,
    "StoppingCritical": 2,
}


def parse_hyperv_vms(info):
    parsed = {}
    for line in info:
        if len(line) != 4:
            # skip lines containing invalid data like e.g.
            # ../tests/unit/checks/generictests/datasets/hyperv_vms.py, line 16 or 17
            continue
        # Remove quotes
        line = [x.strip('"') for x in line]
        if line[1].endswith("..."):  # broken output
            vm_name = line[0]
            line = line[2:]
        elif line[1].startswith("("):
            idx = 2
            while idx < len(line):
                if line[idx].endswith(")"):
                    vm_name = " ".join(line[: idx + 1])
                    break
                idx += 1
            line = line[idx + 1 :]
        else:
            vm_name = line[0]
            line = line[1:]

        if ":" in line[1]:  # skip heading line
            parsed[vm_name] = {
                "state": line[0],
                "uptime": line[1],
                "state_msg": " ".join(line[2:]),
            }
    return parsed


def inventory_hyperv_vms(parsed):
    return [(vm_name, {"state": vm["state"]}) for (vm_name, vm) in parsed.items()]


@get_parsed_item_data
def check_hyperv_vms(_item, params, vm):
    # compare against discovered VM state
    if params.get("compare_discovery"):
        discovery_state = params.get("state")

        # this means that the check is executed as a manual check
        if discovery_state is None:
            service_state = 3
            message = "State is %s (%s), discovery state is not available" % (
                vm["state"],
                vm["state_msg"],
            )
        elif vm["state"] == discovery_state:
            service_state = 0
            message = "State %s (%s) matches discovery" % (vm["state"], vm["state_msg"])
        else:
            service_state = 2
            message = "State %s (%s) does not match discovery (%s)" % (
                vm["state"],
                vm["state_msg"],
                params["state"],
            )

    # service state defined in rule
    else:
        service_state = params.get(vm["state"])

        # as a precaution, if in the future there are new VM states we do not know about
        if service_state is None:
            service_state = 3
            message = "Unknown state %s (%s)" % (vm["state"], vm["state_msg"])

        else:
            message = "State is %s (%s)" % (vm["state"], vm["state_msg"])

    yield service_state, message


check_info["hyperv_vms"] = LegacyCheckDefinition(
    parse_function=parse_hyperv_vms,
    check_function=check_hyperv_vms,
    discovery_function=inventory_hyperv_vms,
    service_name="VM %s",
    check_ruleset_name="hyperv_vms",
    default_levels_variable="hyperv_vms_default_levels",
)
