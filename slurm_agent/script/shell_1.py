"""
POC

Succeed with the output
---
Run a Flyte SlurmShellTask...

Run a python script /home/ubuntu/abao/tools/test_inputs.py...
Adding 1 to 1...
Result: 2
---

Use _PythonFStringInterpolizer for string interpolation
* Support inputs only, no outputs
* Need to pass inputs as dict ({"x": 1}), but not LiteralMap
    * Converted to LiteralMap in AsyncAgentExecutorMixin._create
    * Convert LiteralMap back to dict then interpolate?
"""
import os

from flytekit import kwtypes, workflow
from flytekitplugins.slurm import Slurm, SlurmShellTask


shell_task = SlurmShellTask(
    name="test-shell",
    script="""#!/bin/bash
# We can define sbatch options here too,
# but using sbatch_conf can be more neat 
echo "Run a Flyte SlurmShellTask...\n"

# Run a demo python script on Slurm
. /home/ubuntu/.cache/pypoetry/virtualenvs/demo-poetry-RLi6T71_-py3.12/bin/activate;
python3 /home/ubuntu/abao/tools/test_inputs.py --x {inputs.x}
""",
    task_config=Slurm(
        slurm_host="aws",
        sbatch_conf={
            "partition": "debug",
            "job-name": "tiny-slurm",
        }
    ),
    inputs=kwtypes(x=int)
)


@workflow
def wf() -> None:
    shell_task(x=1)


if __name__ == "__main__":
    from flytekit.clis.sdk_in_container import pyflyte
    from click.testing import CliRunner

    runner = CliRunner()
    path = os.path.realpath(__file__)

    print(f">>> LOCAL EXEC <<<")
    result = runner.invoke(pyflyte.main, ["run", path, "wf"])
    print(result.output)