"""
---
Virtual env: dev312
---

Run health check before developement, including:
1. Run a single remote execution
2. Inteact with minio s3 bucket
3. Build an image for a task

Narrow down the scope to ensure that any error encountered originate from the
specific issue you’re addressing, rather than unrelated factors like incorrect
configurations, failed S3 authentication, or similar issues.

* [ ] Make sure minio has the file to read
* [ ] Support more req types for interacting with s3
* [ ] Support external s3 storage (e.g., aws)

## Problems
* Must set interactive to True in FlyteRemote, why? 
    * Read https://docs.flyte.org/en/latest/api/flytekit/design/control_plane.html
* Can't build image through ImageSpec now
    * Build and "push" it to registry before dev for now
"""
import os
import subprocess
from datetime import datetime
from pathlib import Path

import pandas as pd
from flytekit import task, workflow, ImageSpec, WorkflowExecutionPhase
from flytekit.configuration import Config, ImageConfig
from flytekit.remote.remote import FlyteRemote
from flytekit.types.file import FlyteFile
from flytekit.types.structured import StructuredDataset
from flytekit.clis.sdk_in_container import pyflyte


class CFG:
    CONFIG = os.environ.get("FLYTECTL_CONFIG", str(Path.home() / ".flyte" / "config-sandbox.yaml"))
    PROJECT = "flytesnacks"
    DOMAIN = "development"
    IMAGE = os.environ.get("FLYTEKIT_IMAGE", "localhost:30000/flytekit:dev")
    VER = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    image = ImageSpec(
        packages=["pandas", "pyarrow"],
        apt_packages=["git"],
        registry="localhost:30000"
    )


@task
def _tiny_task(msg: str = "dummy") -> str:
    return msg 


@task
def _read_sd(uri: str) -> StructuredDataset:
    sd = StructuredDataset(uri=uri, file_format="parquet")
    print("StructuredDataset df\n---")
    print(sd.open(pd.DataFrame).all())

    return sd


@task
def _read_ff(uri: str) -> FlyteFile:
    ff = FlyteFile(uri)
    print("\nFlyteFile text file\n---")
    with open(ff, "r") as f:
        print(f.read())

    return ff


@task(container_image=CFG.image)
def _build_iamge(dummy: str) -> str:
    print(dummy)
    return dummy


@workflow
def _tiny_wf(msg: str = "dummy") -> str:
    return _tiny_task(msg=msg)


@workflow
def _s3_wf(sd_uri: str, ff_uri: str) -> None:
    _read_sd(uri=sd_uri)
    _read_ff(uri=ff_uri)


@workflow
def _image_wf(dummy: str) -> str:
    return _build_iamge(dummy=dummy)


def check_remote_run() -> None:
    """Check a tiny workflow remote run.

    This function checks:
    1. Whether the remote run succeeds
    2. Whether the workflow output matches the expected
    """
    MSG = "dummy"

    remote = FlyteRemote(Config.auto(config_file=CFG.CONFIG), CFG.PROJECT, CFG.DOMAIN, interactive_mode_enabled=True)
    wf_exec = remote.execute(
        _tiny_wf,
        inputs={"msg": MSG},
        wait=True,
        version=CFG.VER,
        image_config=ImageConfig.from_images(CFG.IMAGE),
    )
    assert wf_exec.closure.phase == WorkflowExecutionPhase.SUCCEEDED, f"Execution failed with phase: {wf_exec.closure.phase}"
    assert wf_exec.outputs["o0"] == MSG, (
        f"Workflow tiny_wf has a wrong output {wf_exec.outpus['o0']}, expect {MSG}."
    )


def check_s3_access() -> None:
    """Check interaction with minio s3 bucket.

    We must ensure both local and remote executions can access the minio s3
    bucket.

    This check should includes multiple request types:
    1. GET: Download a file
    # 2. POST: Upload a file
    # 3. DELETE: Delete a file

    We focus only on GET now.
    """
    SD_URI = "s3://my-s3-bucket/df.parquet"
    FF_URI = "s3://my-s3-bucket/test.txt"

    print("Run local execution...")
    _s3_wf(sd_uri=SD_URI, ff_uri=FF_URI)

    print("Run remote execution...")
    remote = FlyteRemote(Config.auto(config_file=CFG.CONFIG), CFG.PROJECT, CFG.DOMAIN, interactive_mode_enabled=True)
    wf_exec = remote.execute(
        _s3_wf,
        inputs={"sd_uri": SD_URI, "ff_uri": FF_URI},
        wait=True,
        version=CFG.VER,
        image_config=ImageConfig.from_images(CFG.IMAGE),
    )
    assert wf_exec.closure.phase == WorkflowExecutionPhase.SUCCEEDED, f"Execution failed with phase: {wf_exec.closure.phase}"


def check_image_build() -> None:
    # No image build for local, just run a local exec in the activate virtual env?
    print("Run local execution...")
    _ = _image_wf(dummy="hi")

    # print("Run remote execution...")
    # remote = FlyteRemote(Config.auto(config_file=CFG.CONFIG), CFG.PROJECT, CFG.DOMAIN, interactive_mode_enabled=True)
    # wf_exec = remote.execute(
    #     _image_wf,
    #     inputs={"dummy": "hi"},
    #     wait=True,
    #     version=CFG.VER,
    #     image_config=ImageConfig.from_images(CFG.IMAGE),
    # )
    # assert wf_exec.closure.phase == WorkflowExecutionPhase.SUCCEEDED, f"Execution failed with phase: {wf_exec.closure.phase}"


if __name__ == "__main__":
    print(">>> CHECK REMOTE RUN <<<")
    check_remote_run()

    print(">>> CHECK S3 ACCESS <<<")
    check_s3_access()

    print(">>> CHECK IMAGE BUILD <<<")
    check_image_build()

    print(f"=== ALL PASS ===")
    