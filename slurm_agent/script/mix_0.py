import os

from flytekit import workflow
from flytekitplugins.slurm import Slurm, SlurmTask, SlurmRemoteScript, SlurmShellTask


echo_job = SlurmTask(
    name="test-slurm",
    task_config=SlurmRemoteScript(
        slurm_host="aws2",
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
# We can define sbatch options here, but using sbatch_conf can be more neat
echo "Run a Flyte SlurmShellTask...\n"
# Run a python script on Slurm
# Activate the virtual env first if any
# python3 <path_to_python_script>
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