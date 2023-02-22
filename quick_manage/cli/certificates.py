"""
    Certificate management tools
"""
from typing import Dict

import click
from quick_manage.environment import Environment, echo_line, echo_json
from quick_manage.certs import get_cert_info_from_server


@click.group(name="cert", invoke_without_command=True)
@click.pass_context
def cert(ctx: click.core.Context):
    pass


@cert.command()
@click.pass_context
@click.argument("target", type=str)
@click.option("-j", "--json", "json_output", is_flag=True, help="Use JSON output")
def check(ctx: click.core.Context, target: str, json_output):
    """ Check a certificate to get information about it.

    The target may be a hostname, a hostname:port, or a file"""
    env = Environment.default()
    try:
        info = get_cert_info_from_server(target)
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
