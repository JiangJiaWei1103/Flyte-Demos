import os

from flytekit import kwtypes, workflow
from flytekitplugins.slurm import Slurm, SlurmShellTask


write_file_task = SlurmShellTask(
    name="write-file",
    script="""#!/bin/bash

echo "Write an integer..."
echo "Input integer: {inputs.x}" >> ~/write_num.txt
echo "Write a float..."
echo "Input float: {inputs.y}" >> ~/write_num.txt
""",
    task_config=Slurm(
        ssh_config={
            "host": "aws2",
            "username": "ubuntu",
        },
        sbatch_conf={
            "partition": "debug",
            "job-name": "tiny-slurm",
        }
    ),
    inputs=kwtypes(x=int, y=float),
)


@workflow
def wf() -> None:
    write_file_task(x=1, y=1.5)


if __name__ == "__main__":
    from flytekit.clis.sdk_in_container import pyflyte
    from click.testing import CliRunner

    runner = CliRunner()
    path = os.path.realpath(__file__)

    print(f">>> LOCAL EXEC <<<")
    result = runner.invoke(pyflyte.main, ["run", path, "wf"])
    print(result.output)