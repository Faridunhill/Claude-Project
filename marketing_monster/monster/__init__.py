"""MARKETING MONSTER — the loop, as code.

Well -> Digger -> Judge -> Maker -> Mouth -> Scale -> Well

Spec: channel/TO_FARID/003 (evaluation) and 004 (v1.2 build spec).
Pure stdlib by design — it runs on Farid's PC with no installs, the same
property the dating engine has.
"""
from .digger import Digger
from .judge import Judge
from .ledger import AppendOnlyLog, LedgerError
from .maker import Maker
from .playbook import Playbook
from .scale import Scale
from .wall import Cookbook, admission_test
from .well import Well

__all__ = ["AppendOnlyLog", "Cookbook", "Digger", "Judge", "LedgerError",
           "Maker", "Playbook", "Scale", "Well", "admission_test"]
__version__ = "1.2.0"
