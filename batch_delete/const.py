"""
Some reusable constants.
"""
from pathlib import Path 

CONFIG = Path.home() / ".flyte" / "config-sandbox.yaml"
ENDPOINT = "localhost:30080"
PROJECT = "flytesnacks"
DOMAIN = "development"
IMAGE = "localhost:30000/flytekit:dev"