from typing import Optional

from fabric import Connection, Config, Result

from quick_manage import ClientException
from quick_manage.ssh.users import create_user, get_authorized_keys
from quick_manage.ssh.keys import generate_pair


class SSHClient:
    def __init__(self, **kwargs):
        self.sudo_password: Optional[str] = kwargs.get("sudo_password", None)
        self.password: Optional[str] = kwargs.get("password", None)
        self.private_key: Optional[str] = kwargs.get("private_key", None)

        # Prepare connection arguments
        connect_kwargs = {}
        if self.private_key:
            pass
        elif self.password:
            connect_kwargs["password"] = self.password
        else:
            raise ValueError("Must provide either a password or a private key")

        self._conn: Optional[Connection] = None

        # Prepare overrides
        overrides = {}
        if self.sudo_password:
            overrides["sudo"] = {"password": self.sudo_password}

        self.config = Config(overrides=overrides)


def create_remote_admin(username, host, password):
    config = Config(overrides={"sudo": {"password": password}})
    conn = Connection(host=host, user=username,
                      connect_kwargs={"password": password},
                      config=config)

    # admin_name = "matt.jarvis.adm"
    admin_name = "remote_admin"

    # Create the user
    create_user(conn, admin_name)

    # SSH Authorized keys
    public, private = generate_pair()
    existing_keys = get_authorized_keys(conn, admin_name)

    with open(f"{admin_name}-{host}.key", "w") as handle:
        handle.write(private)

    # This is necessary to prepare sudo for the use of | sudo tee
    conn.sudo("ls", pty=True, hide=True)

    if not existing_keys:
        conn.sudo(f"mkdir -p /home/{admin_name}/.ssh", pty=True, hide=True)
        conn.sudo(f"chown {admin_name}:{admin_name} /home/{admin_name}/.ssh", pty=True, hide=True)
        # conn.sudo(f"touch /home/{admin_name}/.ssh/authorized_keys", pty=True, hide=True)

    if public not in existing_keys:
        conn.sudo(f'echo "{public}" | sudo tee -a /home/{admin_name}/.ssh/authorized_keys', pty=True, hide=True)
        conn.sudo(f"chown {admin_name}:{admin_name} /home/{admin_name}/.ssh/authorized_keys", pty=True, hide=True)

    # Passwordless sudo
    conn.sudo(f'echo "{admin_name} ALL = (ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/{admin_name}', pty=True)

    # SSH password disabled
    conn.sudo(
        f'printf "Match User {admin_name}\n\tPasswordAuthentication no\n" | sudo tee /etc/ssh/ssh_config.d/83-{admin_name}.conf',
        pty=True)
