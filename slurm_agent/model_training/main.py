"""
A beautiful MNIST model training example using the Slurm agent.
"""
import os
from typing import Tuple

import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from flytekit import task, workflow
from flytekit.types.file import FlyteFile
from flytekitplugins.slurm import SlurmFunction

from dataset import get_dataset
from model import Model
from trainer import train_epoch, eval_epoch


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
def process_data(raw_data_path: str) -> Tuple[Dataset, Dataset]:
    tr_ds, val_ds = get_dataset(download_path=raw_data_path)

    return tr_ds, val_ds


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
    tr_ds: Dataset,
    val_ds: Dataset,
    epochs: int = 5,
    batch_size: int = 32,
    lr: float = 1e-3,
) -> FlyteFile:
    # Build dataloaders
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
    for ep in range(epochs):
        tr_loss = train_epoch(
            tr_loader=tr_loader, 
            model=model, 
            loss_fn=loss_fn, 
            optimizer=optimizer,
        )
        val_loss, acc = eval_epoch()    

        # Record the model ckpt

    # return weights


# @task
# def run_infer() -> Dict[str, float]:
#     return prf_report


# @workflow
# def dl_wf(
#     raw_data_path: str,
# ) -> Dict[str, float]:
#     tr_ds, val_ds = process_data(raw_data_path=raw_data_path)
#     output_path = train()
#     prf_report = run_infer()
#     return prf_report


if __name__ == "__main__":
    from flytekit.clis.sdk_in_container import pyflyte
    from click.testing import CliRunner

    runner = CliRunner()
    path = os.path.realpath(__file__)

    # Local run
    print(f">>> LOCAL EXEC <<<")
    result = runner.invoke(pyflyte.main, ["run", "--raw-output-data-prefix", "s3://my-flyte-slurm-agent", path, "process_data", "--raw_data_path", "/tmp/torch_data"])
    print(result.output)

