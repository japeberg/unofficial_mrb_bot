# mrb_message.py

import typing as typ
from datetime import datetime


class MRBMessage(typ.NamedTuple):
    title: str
    message: str
    reason: str
    alternatives: str
    line_id: int
    timestamp: datetime