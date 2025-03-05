import os
from typing import Tuple

from flytekit import task, kwtypes, workflow
from flytekit.types.file import FlyteFile
from flytekitplugins.slurm import Slurm, SlurmShellTask
from flytekit.extras.tasks.shell import OutputLocation


@task
def get_file_and_dir() -> Tuple[str, str]:
    x = "/home/ubuntu/demo.txt"
    y = "/home/ubuntu/demo_dir"

    return x, y


@task
def probe(msg: str) -> None:
    print(msg)


write_file_task = SlurmShellTask(
    name="write-file",
    script="""#!/bin/bash

echo "[SlurmShellTask] Write something into a file..." >> {inputs.x}
if grep "file" {inputs.x}
then
    echo "Found a string 'file'!" >> {inputs.x}
else
    echo "'file' not found!"
fi
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
    inputs=kwtypes(x=str),
    output_locs=[OutputLocation(var="i", var_type=FlyteFile, location="{inputs.x}")],
)


cp_zip_task = SlurmShellTask(
    name="cp-zip",
    script="""#!/bin/bash

mkdir {inputs.y}
cp {inputs.x} {inputs.y}
tar -zcvf {outputs.j} {inputs.y}
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
    inputs=kwtypes(x=str, y=str),
    output_locs=[OutputLocation(var="j", var_type=FlyteFile, location="{inputs.y}.tar.gz")],
)


unzip_cat_task = SlurmShellTask(
    name="unzip-cat",
    script="""#!/bin/bash
    
tar -zxvf {inputs.z}
cat {inputs.y}/$(basename {inputs.x}) | wc -m > {outputs.k}
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
    inputs=kwtypes(x=str, y=str, z=str),
    output_locs=[
        OutputLocation(var="k", var_type=FlyteFile, location="output.txt"),
        OutputLocation(var="zip_file", var_type=FlyteFile, location="{inputs.z}")
    ],
)


@workflow
def wf() -> Tuple[str, str]:
    x, y = get_file_and_dir()
    probe(x)
    probe(y)
    t1_out = write_file_task(x=x)
    probe(t1_out)
    t2_out = cp_zip_task(x=t1_out, y=y)
    probe(t2_out)
    out_file, out_zip_file = unzip_cat_task(x=x, y=y, z=t2_out)

    return out_file, out_zip_file 


if __name__ == "__main__":
    from flytekit.clis.sdk_in_container import pyflyte
    from click.testing import CliRunner

    runner = CliRunner()
    path = os.path.realpath(__file__)

    print(f">>> LOCAL EXEC <<<")
    result = runner.invoke(pyflyte.main, ["run", path, "wf"])
    print(result.output)