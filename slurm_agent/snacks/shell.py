"""
Run the user-defined script with optional arguments. 
"""
import os

from flytekit import workflow
from flytekitplugins.slurm import Slurm, SlurmShellTask


shell_task = SlurmShellTask(
    name="shell",
    script="""#!/bin/bash -i

echo [TEST SLURM SHELL TASK 1] Run the user-defined script...
""",
    task_config=Slurm(
        ssh_config={
            "host": "aws2",
            "username": "ubuntu",
        },
        sbatch_conf={
            "partition": "debug",
            "job-name": "job1",
        }
    )
)


shell_task_with_args = SlurmShellTask(
    name="shell",
    script="""#!/bin/bash -i

echo [TEST SLURM SHELL TASK 2] Run the user-defined script with args...
echo Arg1: $1
echo Arg2: $2
echo Arg3: $3
""",
    task_config=Slurm(
        ssh_config={
            "host": "aws2",
            "username": "ubuntu",
        },
        sbatch_conf={
            "partition": "debug",
            "job-name": "job2",
        },
        batch_script_args=["0", "a", "xyz"],
    )
)


@workflow
def wf() -> None:
    shell_task()
    shell_task_with_args()


if __name__ == "__main__":
    from flytekit.clis.sdk_in_container import pyflyte
    from click.testing import CliRunner

    runner = CliRunner()
    path = os.path.realpath(__file__)

    print(f">>> LOCAL EXEC <<<")
    result = runner.invoke(pyflyte.main, ["run", path, "wf"])
    print(result.output)