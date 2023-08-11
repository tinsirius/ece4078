import sys
import importlib

def import_based_on_version(caller_globals=None, caller_locals=None):
    module_name = f".system_{sys.version_info.major}{sys.version_info.minor}"
    module = importlib.import_module(module_name, package="ece4078.localization")

    if caller_globals is None:
        caller_globals = globals()

    if caller_locals is None:
        caller_locals = locals()

    for key, value in module.__dict__.items():
        if not key.startswith('_'):
            caller_globals[key] = value
            caller_locals[key] = value
