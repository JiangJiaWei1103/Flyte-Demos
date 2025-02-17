import os

from flytekit import workflow
from flytekitplugins.slurm import Slurm, SlurmTask, SlurmRemoteScript, SlurmShellTask


echo_job = SlurmTask(
    name="test-slurm",
    task_config=SlurmRemoteScript(
        ssh_config={
            "host": "aws2",
            "username": "ubuntu",
            # "client_keys": ["~/.ssh/slurm_reprod.pem"],
        },
        batch_script_path="/home/ubuntu/test/echo.sh",
        sbatch_conf={
            "partition": "debug",
            "job-name": "tiny-slurm",
        }
    )
)

shell_task = SlurmShellTask(
    name="test-shell",
    script="""#!/bin/bash

echo "Run a Flyte SlurmShellTask...\n"
""",
    task_config=Slurm(
        ssh_config={
            "host": "aws2",
            "username": "ubuntu",
            # "client_keys": ["~/.ssh/slurm_reprod.pem"],
        },
        sbatch_conf={
            "partition": "debug",
            "job-name": "tiny-slurm",
        }
    ),
)


@workflow
def wf():
    echo_job()
    shell_task()


if __name__ == "__main__":
    from flytekit.clis.sdk_in_container import pyflyte
    from click.testing import CliRunner

    runner = CliRunner()
    path = os.path.realpath(__file__)

    # Local run
    print(f">>> LOCAL EXEC <<<")
    result = runner.invoke(pyflyte.main, ["run", path, "wf"])
    print(result.output)