"""Smoke test: import the HAL and behavior modules and run lightweight checks.

This test does not require ROS2 and will only call non-ROS fallback functions.
Run: python -m embodiedControlAgent.tests.smoke_test
"""

from embodiedControlAgent.hal import joint_state_publisher
from embodiedControlAgent.behaviors import demo_bt


def test_imports():
    # instantiate main functions (do not start infinite loops)
    assert hasattr(joint_state_publisher, 'main')
    assert hasattr(demo_bt, 'main')


if __name__ == '__main__':
    print('Running smoke checks...')
    test_imports()
    print('OK - smoke import checks passed')
