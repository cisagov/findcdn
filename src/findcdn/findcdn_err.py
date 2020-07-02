#!/usr/bin/env python3

"""Define public exports."""
__all__ = ["OutputFileExists", "InvalidDomain", "FileWriteError", "NoDomains"]


class NoDomains(Exception):
    """Raise when no domains are passed to findcdn main."""

    def __init__(self, error):
        """Instantiate super class with passed message."""
        self.message = "No domains were passed!"
        super().__init__(self.message)


class OutputFileExists(Exception):
    """Raise when file already exists when writing in findcdn."""

    def __init__(self, outFile):
        """Instantiate super class with passed message with passed in filename."""
        self.message = "A file with the name " + outFile + " already exists!"
        super().__init__(self.message)


class InvalidDomain(Exception):
    """Raise when an invalid domain is inputted in findcnd.main()."""

    def __init__(self, item):
        """Instantiate super class with passed message with passed in item."""
        self.message = item + " is not a valid domain in findcdn.main()"
        super().__init__(self.message)


class FileWriteError(Exception):
    """Raise when there is a problem writing to a file in findcnd."""

    def __init__(self, error):
        """Instantiate super class with passed message using passed in error."""
        self.message = (
            "The following error occurred in findcdn while file writing:\n"
            + repr(error)
        )
        super().__init__(self.message)
