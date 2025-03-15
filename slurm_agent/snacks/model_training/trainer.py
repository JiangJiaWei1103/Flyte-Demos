"""
Define main training logic.

* [ ] Handle `device`
"""
import gc
from typing import Tuple

from tqdm import tqdm

import torch
import torch.nn as nn
from torch.optim import Optimizer
from torch.utils.data import DataLoader


def train_epoch(
    tr_loader: DataLoader,
    model: nn.Module,
    loss_fn: nn.Module,
    optimizer: Optimizer,
    debug: bool = False
) -> float:
    """Run training for one epoch.

    Args:
        tr_loader: Training dataloader.
        model: Model instance.
        loss_fn: Loss criterion.
        optimizer: Optimizer.
        debug: If True, run one batch only.

    Returns:
        The average training loss over batches.
    """
    tr_loss_tot = 0.0

    model.train()
    for i, batch_data in tqdm(enumerate(tr_loader), total=len(tr_loader)):
        optimizer.zero_grad(set_to_none=True)

        # Retrieve batched raw data
        x, y = batch_data
        inputs = {"x": x}

        # Forward pass
        logits = model(inputs)

        # Derive loss
        loss = loss_fn(logits, y)
        tr_loss_tot += loss.item()

        # Backpropagation
        loss.backward()

        optimizer.step()

        del x, y, inputs, logits 
        _ = gc.collect()

        if debug:
            break

    tr_loss_avg = tr_loss_tot / len(tr_loader)

    return tr_loss_avg    


@torch.no_grad()
def eval_epoch(
    eval_loader: DataLoader, 
    model: nn.Module,
    loss_fn: nn.Module,
    debug: bool = False
) -> Tuple[float, float]:
    """Run evaluation for one epoch.

    Args:
        eval_loader: Evaluation dataloader.
        model: Model instance.
        loss_fn: Loss criterion.
        debug: If True, run one batch only.

    Returns:
        A tuple (eval_loss_avg, acc), where eval_loss_avg is the average evaluation loss over batches
        and acc is the accuracy.
    """
    eval_loss_tot = 0
    y_true, y_pred = [], []

    model.eval()
    for i, batch_data in tqdm(enumerate(eval_loader), total=len(eval_loader)):
        # Retrieve batched raw data
        x, y = batch_data
        inputs = {"x": x}

        # Forward pass
        logits = model(inputs)

        # Derive loss
        loss = loss_fn(logits, y)
        eval_loss_tot += loss.item()

        # Record batched output
        y_true.append(y.detach())
        y_pred.append(logits.detach())

        del x, y, inputs, logits 
        _ = gc.collect()

        if debug:
            break

    eval_loss_avg = eval_loss_tot / len(eval_loader)

    # Derive accuracy
    y_true = torch.cat(y_true, dim=0)
    y_pred = torch.cat(y_pred, dim=0)
    y_pred = torch.argmax(y_pred, dim=1)
    acc = (y_true == y_pred).sum() / len(y_true)

    return eval_loss_avg, acc


if __name__ == "__main__":
    from dataset import get_dataset
    from model import Model

    B, C, H, W = 32, 1, 28, 28
    tr_ds, val_ds = get_dataset("./tmp_data")
    tr_loader = DataLoader(tr_ds, batch_size=B, shuffle=True, drop_last=True)
    val_loader = DataLoader(val_ds, batch_size=B*4, shuffle=False, drop_last=False)
    for i, batch_data in enumerate(tr_loader):
        x, y = batch_data
        assert x.shape == torch.Size([B, C, H, W])
        assert y.shape == torch.Size([B, ])

    model = Model()
    loss_fn = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    tr_loss = train_epoch(tr_loader, model, loss_fn, optimizer, debug=True)
    val_loss, acc = eval_epoch(val_loader, model, loss_fn, debug=True)
    print(f"TRAIN LOSS {tr_loss:.4f} | VAL LOSS {val_loss:.4f} | ACC {acc:.4f}")