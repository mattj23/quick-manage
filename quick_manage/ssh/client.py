from dataclasses import dataclass
from io import StringIO
from typing import Optional, Dict

from fabric import Connection, Config, Result
from paramiko import PKey, RSAKey, DSSKey, ECDSAKey, Ed25519Key
from paramiko.ssh_exception import SSHException

from quick_manage import ClientException
from quick_manage.keys import KeyGetter
from quick_manage.ssh.users import create_user, get_authorized_keys
from quick_manage.ssh.keys import private_key_from_string


class SSHClient:
    @dataclass
    class Config:
        user: str
        endpoint: str
        password: Optional[str] = None
        key: Optional[str] = None
        sudo: Optional[str] = None

    def __init__(self, config: Config, key_getter: KeyGetter, nets: Dict[str, str]):
        # self.user = user
        # self.host = host
        # self.sudo_password: Optional[str] = kwargs.get("sudo_password", None)
        # self.password: Optional[str] = kwargs.get("password", None)
        # self.private_key: Optional[str] = kwargs.get("private_key", None)
        # self.key_data: Optional[str] = kwargs.get("key_data", None)
        self.config = config
        self.key_getter = key_getter
        self.nets = nets

        # Prepare connection arguments
        self.connect_kwargs = {}
        if self.config.key:
            pkey, _ = private_key_from_string(self.key_getter.get(self.config.key))
            if pkey is None:
                raise ValueError("Could not create private key from data")
            self.connect_kwargs['pkey'] = pkey
        elif self.config.password:
            self.connect_kwargs["password"] = self.config.password
        else:
            raise ValueError("Must provide either a password or a private key")

        self._conn: Optional[Connection] = None

        # Prepare overrides
        overrides = {}
        if self.config.sudo:
            overrides["sudo"] = {"password": self.config.sudo}

        self.ssh_config = Config(overrides=overrides)

    def connect(self):
        host = self.nets[self.config.endpoint]
        self._conn = Connection(host=host, user=self.config.user,
                                connect_kwargs=self.connect_kwargs,
                                config=self.ssh_config)
        return self._conn


def create_remote_admin(username, host, password, admin_name, public_key):
    config = Config(overrides={"sudo": {"password": password}})
    conn = Connection(host=host, user=username, connect_kwargs={"password": password}, config=config)

    admin_script_content = _remote_admin_linux \
        .replace("replace::admin_name", admin_name) \
        .replace("replace::public_key", public_key)
    admin_file = StringIO(admin_script_content)

    conn.put(admin_file, "configure.sh")
    conn.run("chmod +x configure.sh", pty=True)
    conn.sudo("./configure.sh", pty=True)
    conn.run("rm configure.sh", pty=True)


_remote_admin_linux = r"""#! /bin/bash

ADMIN_NAME="replace::admin_name"
PUBLIC_KEY="replace::public_key"

ADMIN_HOME="/home/$ADMIN_NAME"
ADMIN_SSH="$ADMIN_HOME/.ssh"
AUTH_KEYS="$ADMIN_SSH/authorized_keys"

# Create user
if id "$ADMIN_NAME" &>/dev/null; then
    echo "User $ADMIN_NAME already exists"
else
    echo "Creating user $ADMIN_NAME"
    useradd $ADMIN_NAME
    passwd -l $ADMIN_NAME
    mkdir -p $ADMIN_SSH
    chown $ADMIN_NAME:$ADMIN_NAME $ADMIN_HOME
fi

# Put public key in authorized_keys
if [ -f $AUTH_KEYS ]; then
    echo "Authorized keys file already exists for user"
    if grep -Fxq "$PUBLIC_KEY" $AUTH_KEYS; then
        echo "Authorized keys file already contains public key"
    else
        echo "Adding public key to authorized keys"
        echo "$PUBLIC_KEY" >> $AUTH_KEYS
    fi
else
    echo "Creating authorized keys file"
    echo "$PUBLIC_KEY" > $AUTH_KEYS
fi

# Passwordless sudo
echo "Setting passwordless sudo"
echo "$ADMIN_NAME ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/${ADMIN_NAME}
"""
