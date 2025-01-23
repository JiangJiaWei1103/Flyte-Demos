import os

from flytekit import workflow
from flytekitplugins.slurm import Slurm, SlurmShellTask


shell_task = SlurmShellTask(
    name="test-shell",
    script="""#!/bin/bash
# We can define sbatch options here too,
# but using sbatch_conf can be more neat 
echo "Run a Flyte SlurmShellTask...\n"

# Run a demo python script on Slurm
. /home/ubuntu/.cache/pypoetry/virtualenvs/demo-poetry-RLi6T71_-py3.12/bin/activate;
python3 /home/ubuntu/abao/tools/hello_task.py
""",
    task_config=Slurm(
        slurm_host="aws",
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