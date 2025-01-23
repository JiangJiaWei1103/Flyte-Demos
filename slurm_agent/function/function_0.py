import os

from flytekit import task, workflow
from flytekitplugins.slurm import SlurmFunction 


@task(
    task_config=SlurmFunction(
        slurm_host="aws",
        srun_conf={
            "partition": "debug",
            "job-name": "tiny-slurm",
        }
    )
)
def plus_one(x: int) -> int: 
    return x + 1


@task
def greet(year: int) -> str:
    return f"Hello {year}!!!"


@workflow
def wf(x: int) -> str:
    x = plus_one(x=x)
    msg = greet(year=x)
    return msg


if __name__ == "__main__":
    from flytekit.clis.sdk_in_container import pyflyte
    from click.testing import CliRunner

    runner = CliRunner()
    path = os.path.realpath(__file__)

    # Local run
    print(f">>> LOCAL EXEC <<<")
    result = runner.invoke(pyflyte.main, ["run", "--raw-output-data-prefix", "s3://my-flyte-slurm-agent", path, "wf", "--x", 2024])
    print(result.output)