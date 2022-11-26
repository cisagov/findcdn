"""Initialize all analyzers in folder."""

# Standard Python Libraries
from importlib import util
from importlib.machinery import ModuleSpec
import os.path as path

# Third-Party Libraries
from yaml import safe_load

# Internal Libraries

# Get path where the modules should be
PWD = path.dirname(path.realpath(__file__))

# Load in analyzers config file
with open(f"{PWD}/analyzers.yml", "r") as fp:
    analyzers = safe_load(fp)

ANALYZERS = {}
for analyzer, attribs in analyzers["analyzers"].items():
    spec = util.spec_from_file_location(
        attribs["classname"], f"{PWD}/{attribs['filename']}"
    )
    if spec is not None and type(spec) == ModuleSpec:
        module = util.module_from_spec(spec)
        if spec.loader is not None:
            spec.loader.exec_module(module)
            ANALYZERS[attribs["classname"]] = {
                "class": getattr(
                    module, attribs["classname"]
                )(),  # instantiate the class here
                "arg": attribs["argument"],
                "prio": attribs["priority"],
            }

ARGS = "".join([v["arg"] for _, v in ANALYZERS.items()])
