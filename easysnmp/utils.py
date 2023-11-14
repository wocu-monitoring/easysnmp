from __future__ import unicode_literals, absolute_import

import ipaddress
import string
import re

from .compat import ub, text_type


def strip_non_printable(value):
    """
    Removes any non-printable characters and adds an indicator to the string
    when binary characters are fonud.

    :param value: the value that you wish to strip
    """
    if value is None:
        return None

    # Filter all non-printable characters
    # (note that we must use join to account for the fact that Python 3
    # returns a generator)
    printable_value = "".join(filter(lambda c: c in string.printable, value))

    if printable_value != value:
        if printable_value:
            printable_value += " "
        printable_value += "(contains binary)"

    return printable_value


def tostr(value):
    """
    Converts any variable to a string or returns None if the variable
    contained None to begin with; this function currently supports None,
    unicode strings, byte strings and numbers.

    :param value: the value you wish to convert to a string
    """

    if value is None:
        return None
    elif isinstance(value, text_type):
        return value
    elif isinstance(value, (int, float)):
        return str(value)
    else:
        return ub(value)


def hostname_is_IPv4(hostname):
    try:
        ipaddress.IPv4Address(hostname)
    except ipaddress.AddressValueError:
        return False
    else:
        return True


def hostname_is_IPv6(hostname):
    try:
        ipaddress.IPv6Address(hostname)
    except ipaddress.AddressValueError:
        return False
    else:
        return True


# Use a different regex in case it needs to detect IPv4 or IPv6 and with or without port.
# Expected format for IPv6: [2001:db8:1234:5678::1]:22
def process_connection_string(hostname, remote_port, is_ipv6):
    connection_string_regex = r"^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(?::(\d{1,5}))?$" if not is_ipv6 else r"(?:\[)?([:\w.]+)(?:\])?(?::(\d+))?"
    connection_string = re.match(connection_string_regex, hostname)
    if connection_string:
        if remote_port:
            raise ValueError(
                "a remote port was specified yet the hostname appears "
                "to have a port defined too"
            )
        else:
            hostname, remote_port = connection_string.groups()
            if ":" in hostname and not is_ipv6:
                raise ValueError(
                    f"an invalid {'IPv6' if is_ipv6 else 'IPv4'} address was specified"
                )

    return hostname, remote_port
