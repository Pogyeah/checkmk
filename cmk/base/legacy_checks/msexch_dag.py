#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# Example Output:
# <<<msexch_dag:sep(58)>>>
# RunspaceId                       : d58353f4-f868-43b2-8404-25875841a47b
# Identity                         : Mailbox Database 1\S0141KL
# Name                             : Mailbox Database 1\S0141KL
# DatabaseName                     : Mailbox Database 1
# Status                           : Mounted
# MailboxServer                    : S0141KL
# ActiveDatabaseCopy               : s0141kl
# ActivationSuspended              : False
# ActionInitiator                  : Unknown
# ErrorMessage                     :
# ErrorEventId                     :
# ExtendedErrorInfo                :
# SuspendComment                   :
# SinglePageRestore                : 0
# ContentIndexState                : Healthy
# ContentIndexErrorMessage         :
# CopyQueueLength                  : 0
# ReplayQueueLength                : 0
# LatestAvailableLogTime           :
# LastCopyNotificationedLogTime    :
# LastCopiedLogTime                :
# LastInspectedLogTime             :
# LastReplayedLogTime              :
# LastLogGenerated                 : 0
# LastLogCopyNotified              : 0
# LastLogCopied                    : 0
# LastLogInspected                 : 0
# LastLogReplayed                  : 0
# LogsReplayedSinceInstanceStart   : 0
# LogsCopiedSinceInstanceStart     : 0
# LatestFullBackupTime             : 22.10.2014 21:55:12
# LatestIncrementalBackupTime      :
# LatestDifferentialBackupTime     :
# LatestCopyBackupTime             :
# SnapshotBackup                   : True
# SnapshotLatestFullBackup         : True
# SnapshotLatestIncrementalBackup  :
# SnapshotLatestDifferentialBackup :
# SnapshotLatestCopyBackup         :
# LogReplayQueueIncreasing         : False
# LogCopyQueueIncreasing           : False
# OutstandingDumpsterRequests      : {}
# OutgoingConnections              :
# IncomingLogCopyingNetwork        :
# SeedingNetwork                   :
# ActiveCopy                       : True
#
# RunspaceId                       : d58353f4-f868-43b2-8404-25875841a47b
# Identity                         : Mailbox Database 2\S0141KL
# Name                             : Mailbox Database 2\S0141KL
# DatabaseName                     : Mailbox Database 2
# Status                           : Healthy
# MailboxServer                    : S0141KL
# ActiveDatabaseCopy               : s0142kl
# ActivationSuspended              : False
# ActionInitiator                  : Unknown
# ErrorMessage                     :
# ErrorEventId                     :
# ExtendedErrorInfo                :
# SuspendComment                   :
# SinglePageRestore                : 0
# ContentIndexState                : Healthy
# ContentIndexErrorMessage         :
# CopyQueueLength                  : 0
# ReplayQueueLength                : 0
# LatestAvailableLogTime           : 15.12.2014 13:26:34
# LastCopyNotificationedLogTime    : 15.12.2014 13:26:34
# LastCopiedLogTime                : 15.12.2014 13:26:34
# LastInspectedLogTime             : 15.12.2014 13:26:34
# LastReplayedLogTime              : 15.12.2014 13:26:34
# LastLogGenerated                 : 2527253
# LastLogCopyNotified              : 2527253
# LastLogCopied                    : 2527253
# LastLogInspected                 : 2527253
# LastLogReplayed                  : 2527253
# LogsReplayedSinceInstanceStart   : 15949
# LogsCopiedSinceInstanceStart     : 15945
# LatestFullBackupTime             : 13.12.2014 19:06:54
# LatestIncrementalBackupTime      :
# LatestDifferentialBackupTime     :
# LatestCopyBackupTime             :
# SnapshotBackup                   : True
# SnapshotLatestFullBackup         : True
# SnapshotLatestIncrementalBackup  :
# SnapshotLatestDifferentialBackup :
# SnapshotLatestCopyBackup         :
# LogReplayQueueIncreasing         : False
# LogCopyQueueIncreasing           : False
# OutstandingDumpsterRequests      : {}
# OutgoingConnections              :
# IncomingLogCopyingNetwork        :
# SeedingNetwork                   :
# ActiveCopy                       : False

#   .--dbcopy--------------------------------------------------------------.
#   |                      _ _                                             |
#   |                   __| | |__   ___ ___  _ __  _   _                   |
#   |                  / _` | '_ \ / __/ _ \| '_ \| | | |                  |
#   |                 | (_| | |_) | (_| (_) | |_) | |_| |                  |
#   |                  \__,_|_.__/ \___\___/| .__/ \__, |                  |
#   |                                       |_|    |___/                   |
#   +----------------------------------------------------------------------+


from cmk.base.check_api import LegacyCheckDefinition
from cmk.base.config import check_info


def inventory_msexch_dag_dbcopy(info):
    getit = False
    key = "Status"
    for line in info:
        if len(line) == 2:
            if line[0].strip() == "DatabaseName":
                dbname = line[1].strip()
                getit = True
            elif getit and line[0].strip() == key:
                yield dbname, (key, line[1].strip())
                getit = False


def check_msexch_dag_dbcopy(item, params, info):
    getit = False
    inv_key, inv_val = params
    for line in info:
        if len(line) == 2:
            key, val = (i.strip() for i in line)
            if key == "DatabaseName" and val == item:
                getit = True
            elif getit and key == inv_key:
                if val == inv_val:
                    state = 0
                    infotxt = f"{inv_key} is {val}"
                else:
                    state = 1
                    infotxt = f"{inv_key} changed from {inv_val} to {val}"
                return state, infotxt
    return None


check_info["msexch_dag.dbcopy"] = LegacyCheckDefinition(
    service_name="Exchange DAG DBCopy for %s",
    sections=["msexch_dag"],
    discovery_function=inventory_msexch_dag_dbcopy,
    check_function=check_msexch_dag_dbcopy,
)

# .
#   .--contentindex--------------------------------------------------------.
#   |                      _             _   _           _                 |
#   |       ___ ___  _ __ | |_ ___ _ __ | |_(_)_ __   __| | _____  __      |
#   |      / __/ _ \| '_ \| __/ _ \ '_ \| __| | '_ \ / _` |/ _ \ \/ /      |
#   |     | (_| (_) | | | | ||  __/ | | | |_| | | | | (_| |  __/>  <       |
#   |      \___\___/|_| |_|\__\___|_| |_|\__|_|_| |_|\__,_|\___/_/\_\      |
#   |                                                                      |
#   +----------------------------------------------------------------------+


def inventory_msexch_dag_contentindex(info):
    for line in info:
        if line[0].strip() == "DatabaseName":
            yield line[1].strip(), None


def check_msexch_dag_contentindex(item, _no_params, info):
    getit = False
    for line in info:
        if len(line) == 2:
            key, val = (i.strip() for i in line)
            if key == "DatabaseName" and val == item:
                getit = True
            elif getit and key == "ContentIndexState":
                if val == "Healthy":
                    state = 0
                else:
                    state = 1
                return state, "Status: %s" % val
    return None


check_info["msexch_dag.contentindex"] = LegacyCheckDefinition(
    service_name="Exchange DAG ContentIndex of %s",
    sections=["msexch_dag"],
    discovery_function=inventory_msexch_dag_contentindex,
    check_function=check_msexch_dag_contentindex,
)

# .
#   .--copyqueue-----------------------------------------------------------.
#   |                                                                      |
#   |           ___ ___  _ __  _   _  __ _ _   _  ___ _   _  ___           |
#   |          / __/ _ \| '_ \| | | |/ _` | | | |/ _ \ | | |/ _ \          |
#   |         | (_| (_) | |_) | |_| | (_| | |_| |  __/ |_| |  __/          |
#   |          \___\___/| .__/ \__, |\__, |\__,_|\___|\__,_|\___|          |
#   |                   |_|    |___/    |_|                                |
#   +----------------------------------------------------------------------+

msexch_dag_copyqueue_default_levels = (100, 200)


def inventory_msexch_dag_copyqueue(info):
    for line in info:
        if line[0].strip() == "DatabaseName":
            yield line[1].strip(), msexch_dag_copyqueue_default_levels


def check_msexch_dag_copyqueue(item, params, info):
    warn, crit = params
    getit = False
    for line in info:
        if len(line) == 2:
            key, val = (i.strip() for i in line)
            if key == "DatabaseName" and val == item:
                getit = True
            elif getit and key == "CopyQueueLength":
                infotxt = "Queue length is %d" % int(val)
                if int(val) >= crit:
                    state = 2
                elif int(val) >= warn:
                    state = 1
                else:
                    state = 0
                if state > 0:
                    infotxt += " (warn/crit at %d/%d)" % (warn, crit)
                perfdata = [("length", int(val), warn, crit, 0)]
                return state, infotxt, perfdata
    return None


check_info["msexch_dag.copyqueue"] = LegacyCheckDefinition(
    service_name="Exchange DAG CopyQueue of %s",
    sections=["msexch_dag"],
    discovery_function=inventory_msexch_dag_copyqueue,
    check_function=check_msexch_dag_copyqueue,
    check_ruleset_name="msexch_copyqueue",
)
