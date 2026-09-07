# 2D PID Motion Controller

This ROS 2 package contains a small vehicle simulator and a two-axis controller. The controller uses feedback from depth and horizontal position to produce bounded thrust commands.

## Control model

The node subscribes to `/depth`, `/setpoint_depth`, `/x`, and `/setpoint_x`. It publishes `/thrust_depth` and `/thrust_x`. The loop runs at 20 Hz. The depth channel includes a tunable buoyancy bias. Both outputs are clamped to the simulator range of -4 to 4.

## Run

The simulator depends on pygame. Install it with `sudo apt install python3-pygame` or `pip3 install pygame`. Build the package in a ROS 2 workspace, source the workspace, and run:

```bash
ros2 run assignment2 simulation
ros2 run assignment2 controller
```

The portfolio explanation is available at [`site/projects/pid-controller.html`](../site/projects/pid-controller.html).
