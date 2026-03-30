"""Simple demo behavior script.

This file provides a minimal behavior-like loop that:
- If ROS2 is available, subscribes to `task/goal` (geometry_msgs/PoseStamped) and
  prints simulated behavior steps when a goal is received.
- Otherwise, accepts a CLI goal (x,y) and runs a mock sequence: plan -> execute -> done.

Run as: python behaviors/demo_bt.py or with ROS2: ros2 run ... (if packaged)
"""
import sys
import time

try:
    import rclpy
    from rclpy.node import Node
    from geometry_msgs.msg import PoseStamped
    ROS2_AVAILABLE = True
except Exception:
    ROS2_AVAILABLE = False


def _mock_behavior(goal):
    print(f"[behavior] received goal: {goal}")
    print("[behavior] planning...")
    time.sleep(0.5)
    print("[behavior] executing...")
    time.sleep(1.0)
    print("[behavior] reached goal")


if ROS2_AVAILABLE:
    class DemoBehaviorNode(Node):
        def __init__(self):
            super().__init__('demo_behavior')
            self.sub = self.create_subscription(PoseStamped, 'task/goal', self.on_goal, 10)

        def on_goal(self, msg: PoseStamped):
            goal = (msg.pose.position.x, msg.pose.position.y, msg.pose.position.z)
            _mock_behavior(goal)

    def main():
        rclpy.init()
        node = DemoBehaviorNode()
        try:
            rclpy.spin(node)
        except KeyboardInterrupt:
            pass
        finally:
            node.destroy_node()
            rclpy.shutdown()

else:
    def main():
        if len(sys.argv) >= 3:
            try:
                x = float(sys.argv[1]); y = float(sys.argv[2])
                _mock_behavior((x, y, 0.0))
            except Exception as e:
                print('invalid args', e)
        else:
            print('Usage: python demo_bt.py <x> <y>')


if __name__ == '__main__':
    main()
