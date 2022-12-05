import re

from invoke import UnexpectedExit

from quick_manage import ClientException
from fabric import Connection, Result


def get_users(conn: Connection):
    result: Result = conn.sudo("cat /etc/passwd", pty=True, hide=True)
    if not result.ok:
        raise ClientException("Failed to access /etc/passwd")

    lines = result.stdout.split("\n")
    users = []
    for line in lines:
        fields = line.split(":")
        if len(fields) < 4:
            continue
        users.append(fields[0])
    return users


def create_user(conn: Connection, user_name: str):
    users = get_users(conn)
    if user_name in users:
        # echo_line(styles.warning(f"User {user_name} already exists, skipping creation"))
        return

    # Create the home directory
    try:
        result = conn.sudo(f"useradd {user_name}", pty=True)
    except UnexpectedExit as e:
        if "already exists" in e.result.stdout:
            # echo_line(styles.warning(f"User {user_name} already exists, skipping creation"))
            return
        raise

    # echo_line(styles.visible(f"User {user_name} created"))

    # Create home directory
    conn.sudo(f"mkdir -p /home/{user_name}", pty=True)
    conn.sudo(f"chown {user_name}:{user_name} /home/{user_name}", pty=True)


def get_authorized_keys(conn: Connection, user_name: str):
    try:
        result: Result = conn.sudo(f"cat /home/{user_name}/.ssh/authorized_keys", pty=True, hide=True)
    except UnexpectedExit as e:
        if "no such file or directory" in e.result.stdout.lower():
            return []
        raise

    if not result.ok:
        raise ClientException("Error retrieving existing authorized keys")

    return [line.strip() for line in result.stdout.split("\n") if line.strip().startswith("ssh-")]
