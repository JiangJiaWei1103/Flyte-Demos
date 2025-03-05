import os

from flytekit import workflow
from flytekitplugins.slurm import Slurm, SlurmShellTask


shell_task = SlurmShellTask(
    name="test-shell",
    script="""#!/bin/bash 

echo "Run a Flyte SlurmShellTask...\n"
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
    ),
    # ===
    # No need to do this, we fix this in 
    # https://github.com/flyteorg/flytekit/pull/3159/commits/f10b63283da5fad9de5e1369b1700d459c189ef9
    # inputs={}
    # ===
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