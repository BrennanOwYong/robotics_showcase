from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(package="ros_chat", executable="chat_client.py", output="screen")
    ])
