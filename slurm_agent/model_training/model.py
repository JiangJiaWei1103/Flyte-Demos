"""
Define model architecture.
"""
from typing import Dict

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor


class Model(nn.Module):

    def __init__(self) -> None:
        super(Model, self).__init__()

        self.cnn_encoder = nn.Sequential(
            # Block 1
            nn.Conv2d(in_channels=1, out_channels=16, kernel_size=5, padding=0),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2),
            # Block 2
            nn.Conv2d(in_channels=16, out_channels=32, kernel_size=5, padding=0),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2)
        )
        self.clf = nn.Linear(32 * 4 * 4, 10)
    
    def forward(self, inputs: Dict[str, Tensor]) -> Tensor:
        x = inputs["x"]
        bs = x.size(0)

        x = self.cnn_encoder(x)
        x = x.reshape(bs, -1)
        logits = self.clf(x)

        return logits


if __name__ == "__main__":
    B, C, H, W = 2, 1, 28, 28
    inputs = {"x": torch.rand(B, C, H, W)}

    model = Model()
    logits = model(inputs=inputs)
    assert logits.shape == torch.Size([B, 10])