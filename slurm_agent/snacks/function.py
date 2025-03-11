"""
Run the user-defined functions.
"""
import os

from flytekit import task, workflow
from flytekitplugins.slurm import SlurmFunction 


@task(
    task_config=SlurmFunction(
        ssh_config={
            "host": "aws2",
            "username": "ubuntu",
        },
        sbatch_conf={
            "partition": "debug",
            "job-name": "job3",
            "output": "/home/ubuntu/fn_task.log"
        },
        script="""#!/bin/bash -i

echo [TEST SLURM FN TASK 1] Run the first user-defined task function...

# Setup env vars
export MY_ENV_VAR=123

# Source the virtual env
. /home/ubuntu/.cache/pypoetry/virtualenvs/demo-4A8TrTN7-py3.12/bin/activate 

# Run the user-defined task function
{task.fn}
"""
    )
)
def plus_one(x: int) -> int: 
    print(os.getenv("MY_ENV_VAR"))
    return x + 1


@task(
    task_config=SlurmFunction(
        ssh_config={
            "host": "aws2",
            "username": "ubuntu",
        },
        script="""#!/bin/bash -i

echo [TEST SLURM FN TASK 2] Run the second user-defined task function...

. /home/ubuntu/.cache/pypoetry/virtualenvs/demo-4A8TrTN7-py3.12/bin/activate 
{task.fn}
"""
    )
)
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

    print(f">>> LOCAL EXEC <<<")
    result = runner.invoke(pyflyte.main, ["run", "--raw-output-data-prefix", "s3://my-flyte-slurm-agent", path, "wf", "--x", 2024])
    print(result.output)