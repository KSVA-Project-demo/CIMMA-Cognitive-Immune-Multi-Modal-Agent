"""Lightweight test for the adversarial agent modules.

This script only performs imports and constructs the agent without launching
heavy attack routines. Run it to verify the modules load correctly.
"""
from agentWorkflow import RobotAdversarialAgent
import os


def main():
    # Build an absolute framework path relative to this test file so the test is robust
    base_dir = os.path.dirname(os.path.abspath(__file__))
    framework_src = os.path.abspath(os.path.join(base_dir, '..', 'multiModalAdversarialAttackFramework', 'src'))
    print('Framework src (test):', framework_src)
    agent = RobotAdversarialAgent(framework_src)
    print('RobotAdversarialAgent constructed successfully.')


if __name__ == '__main__':
    main()
