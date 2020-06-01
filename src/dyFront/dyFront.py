#!/usr/bin/env python

"""dyFront is a security research and reporting tool.

dyFront determine what domain names from a passed in list are domain 
frontable (https://en.wikipedia.org/wiki/Domain_fronting) and exports them to a file. 

EXIT STATUS
    This utility exits with one of the following values:
    0   Frontable domains successfully printed to file
    >0  An error occurred.

Usage:
  dyFront file <fileIn> [options]
  dyFront list  <domain>... [options]
  dyFront (-h | --help)

Options:
  -h --help              Show this message.
  --version              Show the current version.
  -o FILE --output=FILE  If specified, then the output file will be set to
                         the specified value. [default: ./frontable.json]


"""

# Standard Python Libraries
import os
import sys
from typing import Any, Dict

# Third-Party Libraries
import docopt
import pkg_resources
from schema import And, Schema, SchemaError, Use, Or
import validators

from ._version import __version__



def main() -> int:
    """Collect the arguments"""
    args: Dict[str, str] = docopt.docopt(__doc__, version=__version__)
    # Validate and convert arguments as needed
    schema: Schema = Schema(
        {
            "--output": And(
                str,
                lambda filename: not os.path.isfile(filename),
                error= "Output file \"" + args["--output"] + "\" already exists!"
            ),
            "<fileIn>" :Or(
                None,
                And(
                    str,
                    lambda filename: os.path.isfile(filename) ,
                    error= "Input file \"" + str(args["<fileIn>"]) + "\" does not exist!"
                )
            ),
            "<domain>" : And(
                list,                
                error= "Please format the domains as a list."
            ),
            str: object,  # Don't care about other keys, if any
        }
    )

    try:
        validated_args: Dict[str, Any] = schema.validate(args)
    except SchemaError as err:
        # Exit because one or more of the arguments were invalid
        print(err, file=sys.stderr)
        return 1
    
    #Add domains to a list
    domainList = []

    if (validated_args["file"] ==  True):
        try:
            with open(validated_args["<fileIn>"]) as f:
                domainList = [line.rstrip() for line in f]
        except IOError as e:
            print("A file error occured: %s" % e, file=sys.stderr)
            return 1
    else:
        domainList = validated_args["<domain>"]
    
    #Validate domains in list
    for item in domainList:
        if (validators.domain(item) is not True):
            print("One or more domains are not valid",file=sys.stderr)
            return 1
    
    print("%d Domains Validated" % len(domainList))
    
    #Look for CDN

    #Check if domain is frontable

    #Run report

    print("Program exited successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
