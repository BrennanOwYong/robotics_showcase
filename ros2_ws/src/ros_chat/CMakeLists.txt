cmake_minimum_required(VERSION 3.8)
project(ros_chat)

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(rclpy REQUIRED)
find_package(std_msgs REQUIRED)
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "srv/RegisterUser.srv"
  "srv/LeaveUser.srv"
)

ament_python_install_package(ros_chat_runtime)

install(PROGRAMS
  ros_chat_runtime/hub_node.py
  ros_chat_runtime/chat_client.py
  scripts/start_node
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

ament_export_dependencies(rosidl_default_runtime)
ament_package()
