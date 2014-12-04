import re
import socket
from flask import current_app

from dns.name import from_unicode


def is_valid_hostname(hostname):
    """Convert domain label into IDN ACE form (handles internationalized
    domains and regular (ascii) domains"""
    hostname = from_unicode(hostname).to_text()

    # stackoverflow.com/a/2532344/1707152
    if len(hostname) > 255:
        return False
    if hostname[-1] == ".":
        hostname = hostname[:-1]  # strip exactly one dot from the right
    allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(x) for x in hostname.split("."))


def is_valid_ip(ip):
    # stackoverflow.com/a/4017219/1707152

    def is_valid_ipv4_address(address):
        try:
            socket.inet_pton(socket.AF_INET, address)
        except AttributeError:
            try:
                socket.inet_aton(address)
            except socket.error:
                return False
            return address.count('.') == 3
        except socket.error:
            return False

        return True

    def is_valid_ipv6_address(address):
        try:
            socket.inet_pton(socket.AF_INET6, address)
        except socket.error:  # not a valid address
            return False
        return True

    return is_valid_ipv4_address(ip) or is_valid_ipv6_address(ip)


def is_valid_rdtype(rdtype):
    return rdtype in current_app.config['SUPPORTED_RDTYPES']
