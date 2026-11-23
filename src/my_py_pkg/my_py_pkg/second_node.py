import rclpy

def main(args=None):
    rclpy.init(args=args)
    node = rclpy.create_node("python_node")
    node.get_logger().info("Hello, Ros2")
    node.destroy_node()
    rclpy.shutdown()

if __name__=="__main__":
    main()