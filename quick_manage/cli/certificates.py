"""
    Certificate management tools
"""
from typing import Dict, Optional

import click

from quick_manage.cli.common import SecretOrEndpointType
from quick_manage.environment import Environment, echo_line, echo_json
from quick_manage.certs import get_cert_info_from_server, CertInfo
from quick_manage.keys import SecretPath


@click.group(name="cert", invoke_without_command=True)
@click.pass_context
def cert(ctx: click.core.Context):
    pass


def _get_info_from_secret(path_text: str) -> Optional[CertInfo]:
    env = Environment.default()

    # Attempt to try to get the certificate as a secret
    try:
        path = SecretPath.from_text(path_text)
        store = env.active_context.key_stores.get(path.store, None)
        if store:
            value = store.get_value(path.secret, "fullchain").encode("utf-8")
            info = CertInfo.from_x509_bytes(value)
            return info
        return None
    except Exception as e:
        return None


@cert.command()
@click.pass_context
@click.argument("target", type=SecretOrEndpointType())
@click.option("-j", "--json", "json_output", is_flag=True, help="Use JSON output")
def check(ctx: click.core.Context, target: str, json_output):
    """ Check a certificate to get information about it.

    The target may be a hostname, a hostname:port, or a secret"""
    env = Environment.default()

    info = _get_info_from_secret(target)

    try:
        info = info or get_cert_info_from_server(target)
    except ConnectionRefusedError:
        if json_output:
            echo_json({"error": "connection refused"})
        else:
            echo_line(env.fail(f"Connection to {target} was refused by the server"), err=True)
        return

    if json_output:
        echo_json(info.serializable())

    else:
        days_left = info.days_remaining()
        output = [
            ("Issuer", info.issuer, env.visible),
            ("Serial", info.serial, None),
            ("Fingerprint", info.fingerprint, None),
            ("Not Before", info.not_before, None),
            ("Not After", info.not_after, None),
            ("Days Remaining", f"{days_left:.0f}", _remaining_format(days_left, env))
        ]

        labels, _, _ = zip(*output)
        longest = max(len(x) for x in labels) + 1
        for label, value, formatter in output:
            label_text = f"{(label + ':'): <{longest}} "
            if formatter:
                echo_line(formatter(label_text), formatter(value))
            else:
                echo_line(label_text, value)


def _remaining_format(days: float, env: Environment):
    if days <= 1:
        return env.fail
    if days <= 20:
        return env.warning
    return None
