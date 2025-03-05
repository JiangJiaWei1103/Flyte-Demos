"""
Echo a message on the Slurm cluster.
"""

import os

from flytekit import kwtypes, workflow
from flytekitplugins.slurm import Slurm, SlurmShellTask


shell_task = SlurmShellTask(
    name="test-shell",
    script="""#!/bin/bash 

echo "Write an integer to a text file..."
echo "Integer: {inputs.x}" >> ~/test_write.txt
echo "Write an str to a text file..."
echo "String: {inputs.y}" >> ~/test_write.txt
echo "Write an float to a text file..."
echo "Float: {inputs.z}" >> ~/test_write.txt
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
    inputs=kwtypes(x=int, y=str, z=float)
)


@workflow
def wf(x: int, y: str, z: float) -> None:
    shell_task(x=x, y=y, z=z)



if __name__ == "__main__":
    from flytekit.clis.sdk_in_container import pyflyte
    from click.testing import CliRunner

    runner = CliRunner()
    path = os.path.realpath(__file__)

    print(f">>> LOCAL EXEC <<<")
    result = runner.invoke(pyflyte.main, ["run", path, "wf", "--x", 1, "--y", "2", "--z", 9.9])
    print(result.output)