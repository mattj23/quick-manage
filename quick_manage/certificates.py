"""
    Certificate management tools
"""
from typing import Dict

import click
import socket
import ssl
import re
from datetime import datetime as DateTime

from quick_manage._styles import styles, echo_line

_server_pattern = re.compile(r"^([\da-zA-Z.\-]+)(:\d+)?$")


@click.group(name="cert", invoke_without_command=True)
@click.pass_context
def cert(ctx: click.core.Context):
    pass


@cert.command()
@click.pass_context
@click.argument("target", type=str)
def check(ctx: click.core.Context, target: str):
    """ Check a certificate to get information about it.

    The target may be a hostname, a hostname:port, or a file"""
    _get_cert_from_server(target)


def _get_cert_from_server(target: str):
    matches = _server_pattern.findall(target)
    if not matches:
        echo_line(styles.fail(f"Could not parse '{target}' as a hostname/port"))
        return

    host_name, port_text = matches[0]
    port = int(port_text.strip(":")) if port_text else 443

    context = ssl.create_default_context()
    connection = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=host_name)
    connection.settimeout(3)

    try:
        connection.connect((host_name, port))
    except ssl.SSLCertVerificationError as e:
        echo_line(styles.fail(f"Certificate Verification Error: {e.verify_message}"))
        return

    info = connection.getpeercert()
    _process_cert_info(info)


def _process_cert_info(info: Dict):
    issuer = {}
    for group in info["issuer"]:
        for item in group:
            issuer[item[0]] = item[1]

    not_after = _cert_date(info["notAfter"])
    not_before = _cert_date(info["notBefore"])
    remaining = not_after - DateTime.now()

    output_items = [
        ("Issuer", "{organizationName}, CN={commonName}, C={countryName}".format(**issuer)),
        ("Serial", info['serialNumber']),
        ("Version", info['version']),
        (f"Not Before", f"{not_before}"),
        (f"Not After", f"{not_before}"),
        (f"Days Remaining", f"{remaining.days:.0f}")
    ]

    longest = max([len(label) for label, _ in output_items]) + 1
    for label, value in output_items:
        label += ":"
        echo_line(f"{label: <{longest}} ", value)


def _cert_date(text: str) -> DateTime:
    return DateTime.strptime(text, "%b %d %H:%M:%S %Y %Z")
