import os

from flytekit import task, workflow
from flytekitplugins.slurm import SlurmFunction 


@task(
    task_config=SlurmFunction(
        slurm_host="aws2",
        sbatch_conf={
            "partition": "debug",
            "job-name": "fn-task",
            "output": "/home/ubuntu/fn_task.log"
        },
        script="""#!/bin/bash

# == Pre-Execution ==
echo "Let's make this task fail..."

# Setup env vars
export MY_ENV_VAR=123

# Activate virtual env
. /home/ubuntu/.cache/pypoetry/virtualenvs/demo-4A8TrTN7-py3.12/bin/activate 

# == Execute Flyte Task Function ==
{task.fn}

# == Post-Execution ==
echo "Success!!"
"""
    )
)
def divide_zero(x: int) -> float: 
    print(os.getenv("MY_ENV_VAR"))
    return x / 0


@task
def greet(year: int) -> str:
    return f"Hello {year}!!!"


@workflow
def wf(x: int) -> str:
    x = divide_zero(x=x)
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