"""
Create N_EXECS long-running workflows.

Use sleep(300) to mimic long-running conditions.
"""
from time import sleep

from flytekit import task, workflow


N_EXECS = 10


@task
def t0(t: float) -> None:
    sleep(t)
    print(f"Task is done.")


@workflow
def wf(t: float) -> None:
    t0(t=t)
    print(f"Wf is done.")


if __name__ == "__main__":
    import os
    from flytekit.clis.sdk_in_container import pyflyte
    from click.testing import CliRunner

    runner = CliRunner()
    path = os.path.realpath(__file__)

    print(f"Creating {N_EXECS} long-running workflows...")
    for _ in range(N_EXECS):
        result = runner.invoke(pyflyte.main, ["run", "--remote", path, "wf", "--t", 300])
        print(result.output)
    