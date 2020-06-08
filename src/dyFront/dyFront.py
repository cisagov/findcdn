#!/usr/bin/env python

"""dyFront is a security research and reporting tool.

dyFront determine what domain names from a passed in list are domain
frontable (https://en.wikipedia.org/wiki/Domain_fronting) and exports them to a file.

EXIT STATUS
    This utility exits with one of the following values:
    0   Frontable domains successfully printed to file
    >0  An error occurred.

Usage:
  dyFront file <fileIn> [-o FILE]
  dyFront list  <domain>... [-o FILE]
  dyFront (-h | --help)

Options:
  -h --help              Show this message.
  --version              Show the current version.
  -o FILE --output=FILE  If specified, then the JSON output file will be
                         set to the specified value.
"""

# Standard Python Libraries
import datetime
import json
import os
import sys
from typing import Any, Dict

# Third-Party Libraries
import docopt
from schema import And, Or, Schema, SchemaError
import validators

# Internal Libraries
from ._version import __version__
from .frontingEngine import check_frontable


def write_json(json_dict: dict, output: str) -> int:
    """Write dict as JSON to output file."""
    try:
        outfile = open(output, "w")  # TODO:(DoctorEww) Update file operation mode
    except Exception as e:
        print("Unable to open output file:\n%s" % (e), file=sys.stderr)
        return 1
    info = json.dumps(json_dict, indent=4, sort_keys=True)
    outfile.write(info)
    outfile.close()
    return 0


def main() -> int:
    """Collect the arguments."""
    args: Dict[str, str] = docopt.docopt(__doc__, version=__version__)
    # Validate and convert arguments as needed
    schema: Schema = Schema(
        {
            "--output": Or(
                None,
                And(
                    str,
                    lambda filename: not os.path.isfile(filename),
                    error='Output file "' + str(args["--output"]) + '" already exists!',
                ),
            ),
            "<fileIn>": Or(
                None,
                And(
                    str,
                    lambda filename: os.path.isfile(filename),
                    error='Input file "' + str(args["<fileIn>"]) + '" does not exist!',
                ),
            ),
            "<domain>": And(list, error="Please format the domains as a list."),
            str: object,  # Don't care about other keys, if any
        }
    )

    try:
        validated_args: Dict[str, Any] = schema.validate(args)
    except SchemaError as err:
        # Exit because one or more of the arguments were invalid
        print(err, file=sys.stderr)
        return 1

    # Add domains to a list
    domain_list = []
    if validated_args["file"]:
        try:
            with open(validated_args["<fileIn>"]) as f:
                domain_list = [line.rstrip() for line in f]
        except IOError as e:
            print("A file error occured: %s" % e, file=sys.stderr)
            return 1
    else:
        domain_list = validated_args["<domain>"]

    # Validate domains in list
    for item in domain_list:
        if validators.domain(item) is not True:
            print(f"{item} is not a valid domain", file=sys.stderr)
            return 1

    print("%d Domains Validated" % len(domain_list))

    domain_dict = {}

    processed_list = check_frontable(domain_list)

    for domain in processed_list:
        domain_dict[domain.url] = {"IP": str(domain.ip)[1:-1],
                                   "cdns": str(domain.cdns)[1:-1],
                                   "cdns_by_names": str(domain.cdns_by_name)[1:-1],
                                   "Status": "Possibly Frontable"
                                   }

    # Run report
    json_dict = {}
    json_dict["date"] = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    json_dict["domains"] = domain_dict  # type: ignore

    if validated_args["--output"] is None:
        print(json_dict)
    else:
        if not write_json(json_dict, validated_args["--output"]):
            return 1

    print("Program exited successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
