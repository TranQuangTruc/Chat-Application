#!/usr/bin/env python3
# server_management.py
# Run: python server_management.py

import socket
import json
import threading
import time

class ServerManager:
    def __init__(self, host='127.0.0.1', port=5556):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        
    def connect(self):
        """Kết nối đến server management"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            print(f" Đã kết nối đến server management tại {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f" Không thể kết nối: {e}")
            return False
    
    def send_command(self, command_data):
        """Gửi lệnh đến server"""
        if not self.connected:
            print(" Chưa kết nối đến server")
            return None
        
        try:
            self.socket.send(json.dumps(command_data).encode('utf-8'))
            
            # Nhận phản hồi
            response = self.socket.recv(4096).decode('utf-8')
            return json.loads(response)
        except Exception as e:
            print(f" Lỗi gửi lệnh: {e}")
            return None
    
    def get_online_users(self):
        """Lấy danh sách user online"""
        response = self.send_command({"type": "get_users"})
        if response:
            users = response.get('users', [])
            count = response.get('count', 0)
            print(f"\n USER ONLINE ({count}):")
            for i, user in enumerate(users, 1):
                print(f"  {i}. {user}")
            print()
        return response
    
    def broadcast_message(self, message):
        """Gửi thông báo toàn hệ thống"""
        response = self.send_command({
            "type": "broadcast", 
            "message": message
        })
        if response and response.get('status') == 'broadcast_sent':
            print(" Đã gửi thông báo toàn hệ thống")
        return response
    
    def shutdown_server(self):
        """Yêu cầu dừng server"""
        confirm = input("  Bạn có chắc muốn dừng server? (y/n): ")
        if confirm.lower() == 'y':
            response = self.send_command({"type": "shutdown"})
            if response and response.get('status') == 'shutting_down':
                print(" Đã gửi yêu cầu dừng server")
            return response
        else:
            print(" Hủy yêu cầu dừng server")
            return None
    
    def show_server_stats(self):
        """Hiển thị thống kê server (giả lập)"""
        users_response = self.get_online_users()
        if users_response:
            count = users_response.get('count', 0)
            print(f" THỐNG KÊ SERVER:")
            print(f"  • User online: {count}")
            print(f"  • Port: 5555 (chat), 5556 (management)")
            print(f"  • Status:  Đang hoạt động")
            print()
    
    def display_help(self):
        """Hiển thị trợ giúp"""
        print("\n CÁC LỆNH QUẢN LÝ SERVER:")
        print("  users       - Hiển thị user online")
        print("  broadcast   - Gửi thông báo toàn hệ thống")
        print("  stats       - Hiển thị thống kê server")
        print("  shutdown    - Dừng server")
        print("  help        - Hiển thị trợ giúp này")
        print("  quit        - Thoát chương")