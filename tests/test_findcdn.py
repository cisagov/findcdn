#!/usr/bin/env pytest -vs
"""Tests for findcdn."""

# Standard Python Libraries
import os
import sys
from unittest.mock import patch

# Third-Party Libraries
import pytest

# cisagov Libraries
import findcdn

# define sources of version strings
RELEASE_TAG = os.getenv("RELEASE_TAG")
PROJECT_VERSION = findcdn.__version__


def test_stdout_version(capsys):
    """Verify that version string sent to stdout agrees with the module version."""
    with pytest.raises(SystemExit):
        with patch.object(sys, "argv", ["bogus", "--version"]):
            findcdn.findcdn.interactive()
    captured = capsys.readouterr()
    assert (
        captured.out == f"{PROJECT_VERSION}\n"
    ), "standard output by '--version' should agree with module.__version__"


def test_running_as_module(capsys):
    """Verify that the __main__.py file loads correctly."""
    with pytest.raises(SystemExit):
        with patch.object(sys, "argv", ["bogus", "--version"]):
            # F401 is a "Module imported but unused" warning. This import
            # emulates how this project would be run as a module. The only thing
            # being done by __main__ is importing the main entrypoint of the
            # package and running it, so there is nothing to use from this
            # import. As a result, we can safely ignore this warning.
            # cisagov Libraries
            import findcdn.__main__  # noqa: F401
    captured = capsys.readouterr()
    assert (
        captured.out == f"{PROJECT_VERSION}\n"
    ), "standard output by '--version' should agree with module.__version__"


@pytest.mark.skipif(
    RELEASE_TAG in [None, ""], reason="this is not a release (RELEASE_TAG not set)"
)
def test_release_version():
    """Verify that release tag version agrees with the module version."""
    assert (
        RELEASE_TAG == f"v{PROJECT_VERSION}"
    ), "RELEASE_TAG does not match the project version"


def test_list_working():
    """Working domain list to test with."""
    with patch.object(
        sys, "argv", ["bogus", "list", "google.com", "facebook.com", "login.gov"]
    ):
        return_code = None
        try:
            return_code = findcdn.findcdn.interactive()
        except SystemExit as sys_exit:
            return_code = sys_exit.code
    assert return_code is None, "interactive() should return successfully"


def test_list_working_double(capsys):
    """Working domain list to test -d with."""
    with patch.object(
        sys,
        "argv",
        ["bogus", "list", "google.com", "facebook.com", "login.gov", "-v", "-d"],
    ):
        return_code = None
        try:
            return_code = findcdn.findcdn.interactive()
        except SystemExit as sys_exit:
            return_code = sys_exit.code
        captured = capsys.readouterr()
    assert return_code is None, "interactive() should return successfully"
    assert "6 jobs completed" in captured.out


def test_list_working_verbose(capsys):
    """Working domain list to test -v with."""
    with patch.object(
        sys,
        "argv",
        [
            "bogus",
            "list",
            "google.com",
            "facebook.com",
            "superfake.thisisnotarealwebsiteforsure.com",
            "-v",
        ],
    ):
        return_code = None
        try:
            return_code = findcdn.findcdn.interactive()
        except SystemExit as sys_exit:
            return_code = sys_exit.code
        captured = capsys.readouterr()
    assert return_code is None, "interactive() should return successfully"
    assert "3 Domains Validated" in captured.out


def test_list_working_tcount(capsys):
    """Working domain list to test -t with."""
    with patch.object(
        sys,
        "argv",
        ["bogus", "list", "google.com", "facebook.com", "login.gov", "-t", "3", "-v"],
    ):
        return_code = None
        try:
            return_code = findcdn.findcdn.interactive()
        except SystemExit as sys_exit:
            return_code = sys_exit.code
        captured = capsys.readouterr()
    assert return_code is None, "interactive() should return successfully"
    assert "Using 3 threads" in captured.out


def test_list_broken():
    """Broken domain list to test with."""
    with patch.object(
        sys,
        "argv",
        ["bogus", "list", "google.com/searchtest", "facebook.com", "login.gov"],
    ):
        return_code = None
        try:
            return_code = findcdn.findcdn.interactive()
        except SystemExit as sys_exit:
            return_code = sys_exit.code
    assert return_code == 3, "interactive() should return failure"


def test_file_working():
    """Working domain file to test with."""
    with patch.object(sys, "argv", ["./findcdn", "file", "tests/validTest.txt"]):
        return_code = None
        try:
            return_code = findcdn.findcdn.interactive()
        except SystemExit as sys_exit:
            return_code = sys_exit.code
    assert return_code is None, "interactive() should return successfully"


"""Test a broken domains passed in as a file"""


def test_file_broken():
    """Broken domain file to test with."""
    with patch.object(sys, "argv", ["bogus", "file", "tests/invalidTest.txt"]):
        return_code = None
        try:
            return_code = findcdn.findcdn.interactive()
        except SystemExit as sys_exit:
            return_code = sys_exit.code
    assert return_code is not None, "interactive() should return failure"


def test_file_dne():
    """Working domain list to test with."""
    with patch.object(sys, "argv", ["./findcdn", "file", "nosuchfile.txt"]):
        return_code = None
        try:
            return_code = findcdn.findcdn.interactive()
        except SystemExit as sys_exit:
            return_code = sys_exit.code
    assert return_code is not None, "interactive() should return successfully"


def test_file_write(tmpdir):
    """Test writing to a file."""
    file = tmpdir.join("outputtest.txt")
    with patch.object(
        sys, "argv", ["./findcdn", "list", "google.com", "-o", str(file)]
    ):
        findcdn.findcdn.interactive()
    assert "google.com" in file.read()
