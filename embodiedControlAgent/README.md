# embodiedControlAgent (scaffold)

This folder contains the initial scaffold for an embodied control agent meant to interface with humanoid robot hardware or simulation. The goal is to provide a clean HAL, controllers, planners, perception glue, and behavior orchestration.

What is included in this scaffold (Phase 0):

- `hal/joint_state_publisher.py` — simple example publisher that uses ROS2 if available, otherwise runs a local simulation-print loop.
- `behaviors/demo_bt.py` — minimal behavior script that accepts a goal and runs a mock plan/execute sequence. Works with or without ROS2.
- `tests/smoke_test.py` — smoke import tests to ensure modules load without syntax errors.

How to run smoke checks (local, no ROS2 required):

```powershell
python -m embodiedControlAgent.tests.smoke_test
```

If you have ROS2 installed and sourced, you can run the nodes directly (example):

```powershell
python hal/joint_state_publisher.py
python behaviors/demo_bt.py 1.0 2.0
```

