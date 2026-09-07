#!/usr/bin/env python3
"""Interactive ROS 2 terminal client for the background hub."""

import argparse
import json
import os
import select
import signal
import sys
import termios
import time
import tty

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from ros_chat_runtime.common import (BROADCAST_TOPIC, LEAVE_SERVICE,
                             REGISTER_SERVICE, MAX_HISTORY, USERS_TOPIC,
                             ansi, message_json, start_hub_if_missing)
from ros_chat.srv import LeaveUser, RegisterUser


class ChatClient(Node):
    def __init__(self, requested_name):
        super().__init__("ros_chat_client")
        if not start_hub_if_missing(self):
            raise RuntimeError("ROS CHAT HUB was not discovered or started")
        self.user_id = "registering"
        self.color = "white"
        self.users = []
        self.history = []
        self.stop_requested = False
        self.input_text = ""
        self.dirty = True
        self.create_subscription(String, USERS_TOPIC, self.on_users, 10)
        self.create_subscription(String, BROADCAST_TOPIC, self.on_broadcast, 50)
        self.register = self.create_client(RegisterUser, REGISTER_SERVICE)
        self.leave_client = self.create_client(LeaveUser, LEAVE_SERVICE)
        while rclpy.ok() and not self.register.wait_for_service(timeout_sec=1.0):
            self.get_logger().info("Waiting for ROS CHAT HUB...")
        request = RegisterUser.Request()
        request.requested_name = requested_name or ""
        future = self.register.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        result = future.result()
        if result is None or not result.ok:
            raise RuntimeError(result.error if result else "hub registration failed")
        self.user_id = result.user_id
        self.color = result.color
        self.outbound = self.create_publisher(String, result.outbound_topic, 50)
        self.users = [{"user_id": self.user_id, "color": self.color}]
        self.active_users = result.active_users
        self.history = json.loads(result.history_json) + self.history
        self.history = self.history[-MAX_HISTORY:]
        self.get_logger().info("Assigned user ID {} with {} text".format(self.user_id, self.color))

    def on_broadcast(self, message):
        try:
            item = json.loads(message.data)
            if item.get("kind") not in ("chat", "system", "telemetry"):
                return
            if "text" not in item:
                return
            self.add_history_item(item)
        except (ValueError, TypeError):
            return

    def add_history_item(self, item):
        """Store chat and system records in the same CLI display history."""
        self.history.append(item)
        self.history = self.history[-MAX_HISTORY:]
        self.dirty = True

    def on_users(self, message):
        try:
            self.users = json.loads(message.data)
            self.active_users = len(self.users)
            self.dirty = True
        except (ValueError, TypeError):
            return

    def send_message(self, text):
        if text.strip():
            text = text.strip()
            self.outbound.publish(String(data=message_json(
                "chat", user_id=self.user_id, text=text)))

    def render(self):
        print("\033[2J\033[H", end="")
        print("ROS GROUP CHAT | connected through ROS 2 discovery")
        print("Your user ID: {}{}\033[0m".format(ansi(self.color), self.user_id))
        print("Online users ({}): {}".format(
            self.active_users, ", ".join(user["user_id"] for user in self.users)))
        print("Type your message: {}\u2588".format(self.input_text))
        print()
        print("Latest {} chat messages and system events".format(len(self.history)))
        print("-" * 60)
        display_events = list(self.history)
        display_events.sort(key=lambda item: item.get("timestamp", 0))
        for item in display_events:
            if item.get("kind") == "system":
                print("\033[90m[SYSTEM] {}\033[0m".format(item["text"]))
                continue
            if item.get("kind") == "telemetry":
                code = item.get("code", "telemetry")
                print("\033[33m[TELEMETRY:{}] {}: {}\033[0m".format(
                    code, item["user_id"], item["text"]))
                continue
            # Own messages are always white. Remote messages use the colour
            # assigned to their user ID by the hub.
            color = "white" if item["user_id"] == self.user_id else item.get("color", "white")
            print("{}[{}]\033[0m {}".format(ansi(color), item["user_id"], item["text"]))
        print("-" * 60)
        print("Press Enter to send. Ctrl-C exits.", flush=True)
        self.dirty = False

    def poll_input(self):
        if not sys.stdin.isatty():
            return
        ready, _, _ = select.select([sys.stdin], [], [], 0)
        if not ready:
            return
        character = os.read(sys.stdin.fileno(), 1).decode("utf-8", errors="ignore")
        if character in ("\r", "\n"):
            self.send_message(self.input_text)
            self.input_text = ""
        elif character in ("\b", "\x7f"):
            self.input_text = self.input_text[:-1]
            self.dirty = True
        elif character and character != "\x1b":
            self.input_text += character
            self.dirty = True

    def leave(self):
        """Tell the hub to remove this user before the ROS context closes."""
        if self.user_id == "registering" or not rclpy.ok():
            return
        if not self.leave_client.wait_for_service(timeout_sec=1.0):
            return
        request = LeaveUser.Request()
        request.user_id = self.user_id
        future = self.leave_client.call_async(request)
        rclpy.spin_until_future_complete(self, future, timeout_sec=2.0)

    def run(self):
        old_terminal = None
        if sys.stdin.isatty():
            old_terminal = termios.tcgetattr(sys.stdin.fileno())
            tty.setcbreak(sys.stdin.fileno())
        next_heartbeat = 0.0
        try:
            while rclpy.ok() and not self.stop_requested:
                self.poll_input()
                now = time.monotonic()
                if now >= next_heartbeat:
                    self.outbound.publish(String(data=message_json(
                        "heartbeat", user_id=self.user_id)))
                    next_heartbeat = now + 2.0
                rclpy.spin_once(self, timeout_sec=0.05)
                if self.dirty:
                    self.render()
        finally:
            if old_terminal is not None:
                termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_terminal)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", default="", help="Optional display name")
    args = parser.parse_args()
    rclpy.init()
    client = ChatClient(args.name)
    signal.signal(signal.SIGINT, lambda _signum, _frame: setattr(client, "stop_requested", True))
    signal.signal(signal.SIGTERM, lambda _signum, _frame: setattr(client, "stop_requested", True))
    try:
        client.run()
    except KeyboardInterrupt:
        pass
    finally:
        client.leave()
        client.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
