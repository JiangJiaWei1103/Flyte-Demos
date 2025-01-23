import os

from flytekit import workflow
from flytekitplugins.slurm import SlurmRemoteScript, SlurmTask



echo_task = SlurmTask(
    name="check-basic",
    task_config=SlurmRemoteScript(
        slurm_host="aws",
        batch_script_path="/home/ubuntu/abao/tools/echo.sh",
        sbatch_conf={
            "partition": "debug",
            "job-name": "tiny-slurm",
        }
    )
)


@workflow
def wf() -> None:
    echo_task()


if __name__ == "__main__":
    from flytekit.clis.sdk_in_container import pyflyte
    from click.testing import CliRunner

    runner = CliRunner()
    path = os.path.realpath(__file__)

    print(f">>> LOCAL EXEC <<<")
    result = runner.invoke(pyflyte.main, ["run", path, "wf"])
    print(result.output)