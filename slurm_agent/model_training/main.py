"""
A beautiful MNIST model training example using the Slurm agent.

* Uploading and downloading processed datasets take too much time.
"""
import os
from pathlib import Path
from tqdm import tqdm
from typing import Dict, Optional

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from flytekit import task, workflow, ImageSpec
from flytekit.types.file import FlyteFile
from flytekitplugins.slurm import SlurmFunction

from dataset import get_dataset
from model import Model
from trainer import train_epoch, eval_epoch


flytekit_hash = "master"
flytekit = f"git+https://github.com/flyteorg/flytekit.git@{flytekit_hash}"
slurm_agent = f"git+https://github.com/flyteorg/flytekit.git@{flytekit_hash}#subdirectory=plugins/flytekit-slurm"

image = ImageSpec(
    packages=[flytekit, slurm_agent, "torch", "torchvision"],
    apt_packages=["git"],
    registry="localhost:30000"
)


@task(
    task_config=SlurmFunction(
        ssh_config={
            "host": "aws2",
            "username": "ubuntu",
        },
        sbatch_conf={
            "partition": "debug",
            "job-name": "process-data",
            "output": "/home/ubuntu/dp.log"
        },
        script="""#!/bin/bash -i

. /home/ubuntu/.cache/pypoetry/virtualenvs/demo-4A8TrTN7-py3.12/bin/activate 

echo "Process and build torch datasets..."
{task.fn}
"""
    )
)
def process_data(raw_data_path: str) -> str:
    # Bypass data preprocessing here
    # tr_ds, val_ds = get_dataset(download_path=raw_data_path)
    # return tr_ds, val_ds
    proc_data_path = raw_data_path

    return proc_data_path


@task(
    task_config=SlurmFunction(
        ssh_config={
            "host": "aws2",
            "username": "ubuntu",
        },
        sbatch_conf={
            "partition": "debug",
            "job-name": "train-model",
            "output": "/home/ubuntu/train.log"
        },
        script="""#!/bin/bash -i

. /home/ubuntu/.cache/pypoetry/virtualenvs/demo-4A8TrTN7-py3.12/bin/activate 

echo "Run main training and evaluation processes..."
{task.fn}
"""
    )
)
def train(
    data_path: str,
    epochs: int = 5,
    batch_size: int = 32,
    lr: float = 1e-3,
    ckpt_path: Optional[str] = None,
    debug: bool = False,
) -> FlyteFile:
    ckpt_path = Path("./output") if ckpt_path is None else Path(ckpt_path)
    ckpt_path.mkdir(exist_ok=True)
    model_path = ckpt_path / "model.pth"

    # Build dataloaders
    tr_ds, val_ds = get_dataset(download_path=data_path)
    tr_loader = DataLoader(tr_ds, batch_size=batch_size, shuffle=True, drop_last=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size*4, shuffle=False)

    # Build model
    model = Model()

    # Builc loss criterion
    loss_fn = nn.CrossEntropyLoss()

    # Build solvers 
    # Optimizer
    optimizer = optim.Adam(model.parameters(), lr=lr)
    # LR scheduler
    lr_skd = None

    # Run training and evaluation
    best_score = 1e16
    for ep in range(epochs):
        tr_loss = train_epoch(
            tr_loader=tr_loader, 
            model=model, 
            loss_fn=loss_fn, 
            optimizer=optimizer,
            debug=debug,
        )
        val_loss, acc = eval_epoch(eval_loader=val_loader, model=model, loss_fn=loss_fn, debug=debug)

        # Save model ckpt
        if val_loss < best_score:
            best_score = val_loss
            torch.save(model.state_dict(), model_path)

        print(f"Epoch [{ep+1}/{epochs}] TRAIN LOSS {tr_loss:.4f} | VAL LOSS {val_loss:.4f} | ACC {acc:.4f}")

    return FlyteFile(path=model_path)


@task(image=image)
@torch.no_grad()
def run_infer(data_path: str, model_path: FlyteFile) -> Dict[str, float]:
    # Build validation dataloader
    _, val_ds = get_dataset(download_path=data_path)
    val_loader = DataLoader(val_ds, batch_size=2048, shuffle=False)

    # Load model
    model = Model()
    model.load_state_dict(torch.load(model_path.download()))

    y_true, y_pred = [], []
    model.eval()
    for i, batch_data in tqdm(enumerate(val_loader), total=len(val_loader)):
        # Retrieve batched raw data
        x, y = batch_data
        inputs = {"x": x}

        # Forward pass
        logits = model(inputs)

        # Record batched output
        y_true.append(y.detach())
        y_pred.append(logits.detach())

    # Derive accuracy
    y_true = torch.cat(y_true, dim=0)
    y_pred = torch.cat(y_pred, dim=0).argmax(dim=1)
    prf_report = {"acc": ((y_true == y_pred).sum() / len(y_true)).item()}

    return prf_report


@workflow
def dl_wf(
    raw_data_path: str,
    epochs: int = 1,
    debug: bool = True,
) -> Dict[str, float]:
    proc_data_path = process_data(raw_data_path=raw_data_path)
    output_path = train(data_path=proc_data_path, epochs=epochs, debug=debug)
    prf_report = run_infer(data_path=proc_data_path, model_path=output_path)

    return prf_report


if __name__ == "__main__":
    from flytekit.clis.sdk_in_container import pyflyte
    from click.testing import CliRunner

    runner = CliRunner()
    path = os.path.realpath(__file__)

    # Local run
    print(f">>> LOCAL EXEC <<<")
    result = runner.invoke(pyflyte.main, ["run", "--raw-output-data-prefix", "s3://my-flyte-slurm-agent", path, "dl_wf", "--raw_data_path", "/tmp/torch_data"])
    print(result.output)
