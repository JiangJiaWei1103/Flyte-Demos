"""
Process data and build torch datasets.
"""
from typing import Tuple

from torch.utils.data import Dataset
from torchvision import datasets, transforms


RAW_DATA_PATH = "/tmp/torch_data"


def get_dataset(download_path: str = RAW_DATA_PATH) -> Tuple[Dataset, Dataset]:
    """Process data and build training and validation sets.
    
    Args:
        download_path: Directory to store the raw data.    

    Returns:
        A tuple (tr_ds, val_ds), where tr_ds is a training set and val_ds is a valiation set.
    """
    # Define data processing pipeline
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5,), (0.5,))
    ])

    tr_ds = datasets.MNIST(
        root=download_path, train=True, download=True, transform=transform
    )
    val_ds = datasets.MNIST(
        root=download_path, train=True, download=True, transform=transform
    )

    return tr_ds, val_ds


if __name__ == "__main__":
    tr_ds, val_ds = get_dataset("./tmp_data")
    print(f"#Training samples {len(tr_ds)} | #Validation samples {len(val_ds)}")

    x, y = tr_ds[0]
    print(f"Sample: x shape {x.shape} | label {y}")
