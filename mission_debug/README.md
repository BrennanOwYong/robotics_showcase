# Mission execution and debugging

This folder records design work around autonomous underwater missions. The focus is the boundary between behaviour-tree logic, ROS 2 actions, perception results, and vehicle control.

The key engineering question is: when a mission succeeds, retries, or falls back, can an operator explain which stage and decision caused the result?

The portfolio page summarises the mission structure and the observability model: stage IDs, attempt IDs, branch decisions, action correlation, and fallback reasons.

Local analysis and cloned dependency trees are intentionally excluded from the public repository. They contain machine-specific notes and third-party working copies.
