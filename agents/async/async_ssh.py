import os

import asyncio
import asyncssh
from asyncssh import SSHClientConnectionOptions


# Define a tiny bash script to run on the SSH host
tiny_script = """'#!/bin/bash

echo "Just log something on the SSH host."'
"""


async def test_ssh_by_key():
    try:
        async with asyncssh.connect(
            host=os.environ["SSH_HOST"],
            username=os.environ["SSH_USER"],
            options=SSHClientConnectionOptions(client_keys=[os.environ["PRIVATE_KEY_PATH"]])
        ) as conn:
            res1 = await conn.run("echo 'SSH connection through key pair!'", check=True)
            print(f"STDOUT | {res1.stdout}")

            res2 = await conn.run(f"srun -o asyncssh.log bash -c {tiny_script}", check=True)
            assert res2.stdout == "", "STDOUT of srun must be empty."
    except Exception as e:
        print(f"SSH connection failed: {e}")



if __name__ == "__main__":
    asyncio.run(test_ssh_by_key())