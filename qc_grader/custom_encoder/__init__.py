#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# (C) Copyright IBM 2024
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.


import json as JSON

from typing import Any

from qc_grader.custom_encoder.json import GraderJSONEncoder


def to_json(obj: Any, **kwargs) -> str:
    if isinstance(obj, (complex, float, int)):
        return str(obj)
    elif isinstance(obj, str):
        return obj
    else:
        return JSON.dumps(obj, skipkeys=True, cls=GraderJSONEncoder, **kwargs)


def from_json(str: str, **kwargs) -> Any:
    pass
