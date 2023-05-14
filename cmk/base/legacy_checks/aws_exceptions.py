#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


# mypy: disable-error-code="var-annotated"

from cmk.base.check_api import discover_single, LegacyCheckDefinition
from cmk.base.config import check_info

AWSNoExceptionsText = "No exceptions"


def parse_aws_exceptions(info):
    parsed = {}
    for line in info:
        parsed.setdefault(line[0], set()).add(" ".join(line[1:]))
    return parsed


def check_aws_exceptions(item, params, parsed):
    for title, messages in parsed.items():
        errors = [message for message in messages if message != AWSNoExceptionsText]
        if errors:
            yield 2, "%s %s" % (title, ", ".join(errors))
        else:
            yield 0, "%s %s" % (title, AWSNoExceptionsText)


check_info["aws_exceptions"] = LegacyCheckDefinition(
    parse_function=parse_aws_exceptions,
    discovery_function=discover_single,
    check_function=check_aws_exceptions,
    service_name="AWS Exceptions",
)
