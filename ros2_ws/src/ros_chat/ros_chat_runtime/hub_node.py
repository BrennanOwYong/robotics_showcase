#!/usr/bin/env python3
"""Persistent ROS 2 chat hub. It is started in the background by the client."""

import ctypes
import json
import os
import time

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from ros_chat_runtime.common import (BROADCAST_TOPIC, COLORS,
                             HEARTBEAT_TIMEOUT, HUB_NODE_NAME,
                             HUB_PROCESS_NAME, MAX_HISTORY, PID_FILE,
                             REGISTER_SERVICE, LEAVE_SERVICE,
                             RUN_LOCK_FILE,
                             READY_FILE, STATE_FILE, USERS_TOPIC,
                             outbound_topic,
                             message_json)
from ros_chat.srv import RegisterUser
from ros_chat.srv import LeaveUser


def set_process_name():
    try:
        libc = ctypes.CDLL(None)
        libc.prctl(15, HUB_PROCESS_NAME.encode(), 0, 0, 0)  # PR_SET_NAME
    except (AttributeError, OSError):
        pass


class ChatHub(Node):
    def __init__(self):
        super().__init__(HUB_NODE_NAME)
        self.users = {}
        self.history = []
        self.next_number = 1
        self.load_state()
        self.users_pub = self.create_publisher(String, USERS_TOPIC, 10)
        self.broadcast_pub = self.create_publisher(String, BROADCAST_TOPIC, 50)
        self.client_subscriptions = {}
        self.create_service(RegisterUser, REGISTER_SERVICE, self.register_user)
        self.create_service(LeaveUser, LEAVE_SERVICE, self.leave_user)
        self.create_timer(2.0, self.expire_users)
        self.stop_requested = False
        with open(PID_FILE, "w", encoding="utf-8") as stream:
            stream.write(str(os.getpid()))
        with open(READY_FILE, "w", encoding="utf-8") as stream:
            stream.write(str(os.getpid()))
        self.get_logger().info("ROS CHAT HUB running with PID {}".format(os.getpid()))

    def load_state(self):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as stream:
                data = json.load(stream)
            # User records describe the previous session. Clients must
            # register again after a hub restart; do not mark stale terminals
            # as active.
            self.users = {}
            self.history = data.get("history", [])[-MAX_HISTORY:]
            self.next_number = int(data.get("next_number", 1))
        except (OSError, ValueError, TypeError):
            os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)

    def save_state(self):
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        temporary = STATE_FILE + ".{}.tmp".format(os.getpid())
        with open(temporary, "w", encoding="utf-8") as stream:
            json.dump({"users": self.users, "history": self.history,
                       "next_number": self.next_number}, stream)
        os.replace(temporary, STATE_FILE)

    def register_user(self, request, response):
        number = self.next_number
        self.next_number += 1
        user_id = "user-{}".format(number)
        color = COLORS[(number - 1) % len(COLORS)]
        self.users[user_id] = {"number": number, "color": color,
                                "last_seen": time.time()}
        topic = outbound_topic(user_id)
        self.client_subscriptions[user_id] = self.create_subscription(
            String, topic,
            lambda message, sender_id=user_id: self.on_client_message(
                sender_id, message),
            50)
        self.save_state()
        response.ok = True
        response.user_number = number
        response.user_id = user_id
        response.color = color
        response.outbound_topic = topic
        response.history_json = json.dumps(self.history)
        response.active_users = len(self.users)
        response.error = ""
        self.publish_users()
        self.publish_system("{} joined the chat".format(user_id))
        return response

    def on_client_message(self, sender_id, message):
        try:
            payload = json.loads(message.data)
            if payload.get("user_id") != sender_id or sender_id not in self.users:
                return
            self.users[sender_id]["last_seen"] = time.time()
            kind = payload.get("kind")
            if kind == "heartbeat":
                return
            if kind == "chat":
                self.on_chat(sender_id, payload)
            elif kind == "telemetry":
                self.on_telemetry(sender_id, payload)
        except (ValueError, KeyError, TypeError):
            return

    def leave_user(self, request, response):
        if request.user_id not in self.users:
            response.ok = False
            response.error = "unknown user ID"
        else:
            del self.users[request.user_id]
            subscription = self.client_subscriptions.pop(request.user_id, None)
            if subscription:
                self.destroy_subscription(subscription)
            self.save_state()
            response.ok = True
            response.error = ""
            self.publish_users()
            self.publish_system("{} left the chat".format(request.user_id))
        response.active_users = len(self.users)
        if not self.users:
            self.stop_requested = True
        return response

    def on_chat(self, user_id, payload):
        try:
            text = str(payload["text"]).strip()
            if user_id not in self.users or not text:
                return
            item = {"kind": "chat", "user_id": user_id,
                    "color": self.users[user_id]["color"], "text": text,
                    "timestamp": time.time()}
        except (ValueError, KeyError, TypeError):
            return
        self.users[user_id]["last_seen"] = time.time()
        self.history.append(item)
        self.history = self.history[-MAX_HISTORY:]
        self.save_state()
        self.broadcast_pub.publish(String(data=json.dumps(
            item, separators=(",", ":"))))

    def on_telemetry(self, user_id, payload):
        text = str(payload.get("text", "")).strip()
        if not text:
            return
        item = {"kind": "telemetry", "user_id": user_id,
                "color": self.users[user_id]["color"], "text": text,
                "code": str(payload.get("code", "")),
                "timestamp": time.time()}
        self.broadcast_pub.publish(String(data=json.dumps(
            item, separators=(",", ":"))))

    def expire_users(self):
        now = time.time()
        stale = [uid for uid, data in self.users.items()
                 if now - data.get("last_seen", 0) > HEARTBEAT_TIMEOUT]
        for user_id in stale:
            del self.users[user_id]
            subscription = self.client_subscriptions.pop(user_id, None)
            if subscription:
                self.destroy_subscription(subscription)
            self.publish_system("{} left the chat (heartbeat timeout)".format(user_id))
        if stale:
            self.save_state()
            self.publish_users()

    def publish_users(self):
        visible = [{"user_id": uid, "color": data["color"]}
                   for uid, data in sorted(self.users.items())]
        self.users_pub.publish(String(data=json.dumps(visible)))

    def publish_system(self, text):
        self.broadcast_pub.publish(String(data=message_json(
            "system", text=text)))


def claim_run_lock():
    try:
        fd = os.open(RUN_LOCK_FILE, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(str(os.getpid()))
        return True
    except FileExistsError:
        try:
            with open(RUN_LOCK_FILE, "r", encoding="utf-8") as stream:
                old_pid = int(stream.read().strip())
            os.kill(old_pid, 0)
            with open("/proc/{}/comm".format(old_pid), "r", encoding="utf-8") as stream:
                if stream.read().strip() == HUB_PROCESS_NAME:
                    return False
            os.unlink(RUN_LOCK_FILE)
            return claim_run_lock()
        except (OSError, ValueError):
            try:
                os.unlink(RUN_LOCK_FILE)
            except FileNotFoundError:
                pass
            return claim_run_lock()


def main():
    set_process_name()
    if not claim_run_lock():
        return
    rclpy.init()
    node = ChatHub()
    try:
        try:
            while rclpy.ok() and not node.stop_requested:
                rclpy.spin_once(node, timeout_sec=0.2)
        except KeyboardInterrupt:
            pass
    finally:
        node.destroy_node()
        try:
            os.unlink(PID_FILE)
        except FileNotFoundError:
            pass
        try:
            os.unlink(RUN_LOCK_FILE)
        except FileNotFoundError:
            pass
        try:
            os.unlink(READY_FILE)
        except FileNotFoundError:
            pass
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
