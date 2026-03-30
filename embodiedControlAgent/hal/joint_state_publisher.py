"""Simple HAL joint state publisher.

This module provides a tiny example publisher that does one of two things:
- If ROS2 (rclpy) is installed and available, it will create an rclpy node and
  publish sensor_msgs.msg.JointState messages at ~10 Hz.
- Otherwise, it runs a non-ROS fallback that prints simulated joint states to
  stdout at 2 Hz. This allows local testing without a ROS2 installation.

Run as: python hal/joint_state_publisher.py
"""
from time import sleep, time

try:
    import rclpy
    from rclpy.node import Node
    from sensor_msgs.msg import JointState
    ROS2_AVAILABLE = True
except Exception:
    ROS2_AVAILABLE = False


def _simulate_loop(joint_names=None, loop_hz=2.0):
    joint_names = joint_names or ["joint1", "joint2", "joint3"]
    t = 0.0
    dt = 1.0 / loop_hz
    try:
        while True:
            positions = [0.5 * (1.0 + __import__('math').sin(t + i)) for i in range(len(joint_names))]
            ts = time()
            print(f"[sim] t={ts:.3f} joint_states=", dict(zip(joint_names, positions)))
            sleep(dt)
            t += dt
    except KeyboardInterrupt:
        print("[sim] stopped by user")


if ROS2_AVAILABLE:
    class JointStatePublisher(Node):
        def __init__(self):
            super().__init__('joint_state_publisher')
            self.pub = self.create_publisher(JointState, 'robot/joint_states', 10)
            self.joint_names = ['joint1', 'joint2', 'joint3']
            self.timer = self.create_timer(0.1, self._on_timer)
            self.t = 0.0

        def _on_timer(self):
            msg = JointState()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.name = self.joint_names
            msg.position = [0.5 * (1.0 + __import__('math').sin(self.t + i)) for i in range(len(self.joint_names))]
            self.pub.publish(msg)
            self.t += 0.1

    def main():
        rclpy.init()
        node = JointStatePublisher()
        try:
            rclpy.spin(node)
        except KeyboardInterrupt:
            pass
        finally:
            node.destroy_node()
            rclpy.shutdown()

else:
    def main():
        _simulate_loop()


if __name__ == '__main__':
    main()
