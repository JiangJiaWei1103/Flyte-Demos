"""
Run a pre-existing shell script on the Slurm cluster.
"""
import os

from flytekit import workflow
from flytekitplugins.slurm import SlurmRemoteScript, SlurmTask


slurm_task = SlurmTask(
    name="basic",
    task_config=SlurmRemoteScript(
        ssh_config={
            "host": "aws2",
            "username": "ubuntu",
        },
        sbatch_conf={
            "partition": "debug",
            "job-name": "job0",
        },
        batch_script_path="/home/ubuntu/echo.sh",
    )
)


@workflow
def wf() -> None:
    slurm_task()


if __name__ == "__main__":
    from flytekit.clis.sdk_in_container import pyflyte
    from click.testing import CliRunner

    runner = CliRunner()
    path = os.path.realpath(__file__)

    print(f">>> LOCAL EXEC <<<")
    result = runner.invoke(pyflyte.main, ["run", path, "wf"])
    print(result.output)