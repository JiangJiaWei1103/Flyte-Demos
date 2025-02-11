"""
Terminate all executions in RUNNING phase.
"""
from flytekit import FlyteRemote
from flytekit.configuration import Config
from flytekit.models.core.execution import NodeExecutionPhase

from const import CONFIG, PROJECT, DOMAIN


class CFG:
    limit = 10000
    phase = NodeExecutionPhase.RUNNING

REMOTE = FlyteRemote(Config.auto(config_file=str(CONFIG)), PROJECT, DOMAIN, interactive_mode_enabled=False)


if __name__ == "__main__":
    executions, token = REMOTE.client.list_executions_paginated(project=PROJECT, domain=DOMAIN, limit=CFG.limit, token=None)
    for e in executions:
        if e.closure.phase == CFG.phase:
            print(f"e.id.name {e.id.name} | PHASE {e.closure.phase}")
            REMOTE.terminate(e, cause="Terminated manually via script.")