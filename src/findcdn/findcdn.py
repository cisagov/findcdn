"""findcdn is a security research and reporting tool.

findcdn determine what CDN a domain has and prints or exports the results as json.

EXIT STATUS
    This utility exits with one of the following values:
    0   The list of domain's CDNs were successfully exported or printed to a file.
    >0  An error occurred.

Usage:
  findcdn file <fileIn> [options]
  findcdn list  <domain>... [options]
  findcdn (-h | --help)

Options:
  -h --help                    Show this message.
  --version                    Show the current version.
  --checks=<checks>            Select detection types; possible values:
                               cname (c), HTTP headers (h),and whois (w).
                               [default: chw]
  -o FILE --output=FILE        If specified, then the JSON output file will be
                               created at the specified value.
  -v --verbose                 Includes additional print statements.
  --all                        Includes domains with and without a CDN
                               in output.
  -d --double                  Run the checks twice to increase accuracy.
  -t --threads=<thread_count>  Number of threads, otherwise use default. [default: 4]
  --timeout=<timeout>          Max duration in seconds to wait for a domain to
                               conclude processing, otherwise use default. [default: 4]
"""

# Standard Python Libraries
import json
import os
import sys
from typing import Any, Dict, List

# Third-Party Libraries
import docopt
from schema import And, Or, Schema, SchemaError, Use

# Internal Libraries
from ._version import __version__
from .cdnEngine import ARGS, analyze_domains
from .findcdn_err import FileWriteError, InvalidDomain, NoDomains, OutputFileExists

# Global Variables
TIMEOUT = 10  # Time in seconds
THREADS = 10  # If 0 then cdnEngine uses CPU count to set thread count


def write_json(json_dump: str, output: str):
    """Write dict as JSON to output file."""
    try:
        with open(output, "x") as outfile:
            outfile.write(json_dump)
    except FileExistsError:
        raise OutputFileExists(output)
    except Exception as e:
        raise FileWriteError(e)


def main(
    domain_list: List[str],
    checks: str,
    output_path: str = None,
    verbose: bool = False,
    interactive: bool = False,
    threads: int = THREADS,
    timeout: int = TIMEOUT,
    all: bool = False,
) -> str:
    """Take in a list of domains and determine the CDN for each return (JSON, number of successful jobs)."""
    # Check domain list
    results = analyze_domains(
        domains=domain_list,
        checks=checks,
        threads=threads,
        timeout=timeout,
        interactive=interactive,
        verbose=verbose,
    )

    if not all:
        results["valid_domains"] = {
            cdn: v for cdn, v in results["valid_domains"].items() if len(v["cdn"]) > 0
        }

    # Create JSON from the results and return (results, successful jobs)
    json_dump = json.dumps(results, indent=4, sort_keys=False)

    # Show the dump to stdout if verbose or interactive
    if (output_path is None and interactive) or verbose:
        print(json_dump)

    # Export to file if file provided
    if output_path is not None:
        write_json(json_dump, output_path)

    # Return json dump to callee
    return json_dump


def interactive() -> None:
    """Collect command arguments and run the main program."""
    # Obtain arguments from docopt
    args: Dict[str, str] = docopt.docopt(__doc__, version=__version__)

    # Validate and convert arguments as needed with schema
    schema: Schema = Schema(
        {
            "--checks": And(
                Use(str),
                lambda checks: all([c in ARGS for c in checks]),
                error="Check strings must be valid opts.",
            ),
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
            "--threads": And(
                Use(int),
                lambda thread_count: thread_count >= 0,
                error="Thread count must be a positive number",
            ),
            "--timeout": And(
                Use(int),
                lambda timeout: timeout > 0,
                error="The timeout duration must be a number greater than 0",
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
        sys.exit(1)

    # Add domains to a list
    domain_list = []
    if validated_args["file"]:
        try:
            with open(validated_args["<fileIn>"]) as f:
                domain_list = [line.rstrip() for line in f]
        except IOError as e:
            print("A file error occurred: %s" % e, file=sys.stderr)
            sys.exit(1)
    else:
        domain_list = validated_args["<domain>"]

    # Start main runner of program with supplied inputs.
    try:
        main(
            domain_list=domain_list,
            checks=validated_args["--checks"],
            output_path=validated_args["--output"],
            verbose=validated_args["--verbose"],
            interactive=True,  # Launch in interactive mode.
            threads=validated_args["--threads"],
            timeout=validated_args["--timeout"],
            all=validated_args["--all"],
        )
    # Check for all potential exceptions
    except OutputFileExists as ofe:
        print(ofe.message)
        sys.exit(1)
    except FileWriteError as fwe:
        print(fwe.message)
        sys.exit(2)
    except InvalidDomain as invdom:
        print(invdom.message)
        sys.exit(3)
    except NoDomains as nd:
        print(nd.message)
        sys.exit(4)
