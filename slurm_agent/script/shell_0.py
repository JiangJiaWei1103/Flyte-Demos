"""
Echo a message on the Slurm cluster.
"""

import os

from flytekit import workflow
from flytekitplugins.slurm import Slurm, SlurmShellTask


shell_task = SlurmShellTask(
    name="test-shell",
    script="""#!/bin/bash 

echo "Run a Flyte SlurmShellTask with the new interface...\n"
""",
    task_config=Slurm(
        ssh_config={
            "host": "aws2",
            "username": "ubuntu",
            "client_keys": ["~/.ssh/slurm_reprod.pem"],
        },
        sbatch_conf={
            "partition": "debug",
            "job-name": "tiny-slurm",
        }
    )
)


@workflow
def wf() -> None:
    shell_task()



if __name__ == "__main__":
    from flytekit.clis.sdk_in_container import pyflyte
    from click.testing import CliRunner

    runner = CliRunner()
    path = os.path.realpath(__file__)

    print(f">>> LOCAL EXEC <<<")
    result = runner.invoke(pyflyte.main, ["run", path, "wf"])
    print(result.output)