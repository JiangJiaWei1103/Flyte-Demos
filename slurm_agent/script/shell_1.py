import os

from flytekit import workflow
from flytekitplugins.slurm import Slurm, SlurmShellTask


# if -i
# bash: no job control in this shell

shell_task = SlurmShellTask(
    name="test-shell",
    script="""#!/bin/bash

echo "Let's make this task fail...\n"

# Run a demo python script on Slurm
. /home/ubuntu/.cache/pypoetry/virtualenvs/demo-4A8TrTN7-py3.12/bin/activate 
python3 /home/ubuntu/test/raise_err.py
""",
    task_config=Slurm(
        slurm_host="aws2",
        sbatch_conf={
            "partition": "debug",
            "job-name": "tiny-slurm",
        }
    ),
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