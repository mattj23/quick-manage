"""
    Certificate management tools
"""
from typing import Dict

import click
import socket
import ssl
import re
from datetime import datetime as DateTime

from quick_manage.environment import Environment, echo_line
from quick_manage.config import Styles

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
    env: Environment = ctx.obj
    _get_cert_from_server(target, env.config.styles)


def _get_cert_from_server(target: str, styles: Styles):
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
    _process_cert_info(info, styles)


def _process_cert_info(info: Dict, styles: Styles):
    issuer = {}
    for group in info["issuer"]:
        for item in group:
            issuer[item[0]] = item[1]

    not_after = _cert_date(info["notAfter"])
    not_before = _cert_date(info["notBefore"])
    remaining = (not_after - DateTime.now()).days
    remaining_info = (f"Days Remaining", f"{remaining:.0f}")

    output_items = [
        ("Issuer", "{organizationName}, CN={commonName}, C={countryName}".format(**issuer)),
        ("Serial", info['serialNumber']),
        ("Version", info['version']),
        (f"Not Before", f"{not_before}"),
        (f"Not After", f"{not_after}"),
        (f"Days Remaining", f"{remaining:.0f}")
    ]

    longest = max([len(label) for label, _ in output_items]) + 1
    for label, value in output_items[:-1]:
        label += ":"
        echo_line(f"{label: <{longest}} ", value)

    label, value = remaining_info
    label += ":"
    if remaining <= 1:
        echo_line(styles.fail(f"{label: <{longest}} "), styles.fail(value))
    elif remaining <= 20:
        echo_line(styles.warning(f"{label: <{longest}} "), styles.warning(value))
    else:
        echo_line(f"{label: <{longest}} ", value)


def _cert_date(text: str) -> DateTime:
    return DateTime.strptime(text, "%b %d %H:%M:%S %Y %Z")
