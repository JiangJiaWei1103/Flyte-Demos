# Batch Deletion of Executions

## Goal
Enable batch deletion of executions, with optional filtering by node phases

## Use Cases
* Clean up executions queued in bulk
    * e.g., stress testing
* Remove failed executions to free spaces 

## Interface 
### Behavior
* Default: Delete all executions
* Filtered deletion: Delete executions that match a specific node phase

To avoid unintended deletions, a confirmation step may be required.

### Request

### Response

### Error Handling


## References
* [User guide/Nodes](https://docs.flyte.org/en/latest/user_guide/concepts/main_concepts/nodes.html#divedeep-nodes)
* [Flyte Weekly Meeting 2025-01-24 part1](https://youtu.be/FMxkTGiaV7A?t=629)
* [Flyte Weekly Meeting 2025-01-24 part2](https://youtu.be/FMxkTGiaV7A?t=1765)
