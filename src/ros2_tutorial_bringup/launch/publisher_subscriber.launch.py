from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    ld = LaunchDescription()

    publisher_node = Node(
        package="my_py_pkg",
        executable="publisher_node",
        name="publisher_node",
    )

    subscriber_node = Node(
        package="my_py_pkg",
        executable="subscriber_node",
        name="subscriber_node",
    )

    ld.add_action(publisher_node)
    ld.add_action(subscriber_node)
    return ld