#!/usr/bin/env python3
# client_base.py
# A reusable client class + CLI runner.
# Run: python client_base.py --host 127.0.0.1 --port 5555

import socket
import threading
import json
import argparse
from datetime import datetime
from queue import Queue, Empty
import chat_history

DELIM = '\n'

def now_str():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

class ChatClient:
    def __init__(self, username, host='127.0.0.1', port=5555):
        self.username = username
        self.host = host
        self.port = int(port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.recv_thread = None
        self.running = False
        self.recv_queue = Queue()  # queue for received JSON messages
        self._recv_buffer = ''

    def connect(self):
        self.sock.connect((self.host, self.port))
        # send join
        join_msg = {"type": "join", "from": self.username}
        self._send_raw(join_msg)
        # wait for join_ack or rejection
        # start receiver thread
        self.running = True
        self.recv_thread = threading.Thread(target=self._recv_loop, daemon=True)
        self.recv_thread.start()
        # after ack will receive online_list or join_ack
        return True

    def _send_raw(self, obj):
        data = json.dumps(obj, ensure_ascii=False) + DELIM
        self.sock.sendall(data.encode('utf-8'))

    def send_message(self, text, to='all'):
        msg = {"type": "message", "from": self.username, "to": to, "msg": text}
        self._send_raw(msg)
        # save to local history (as outgoing)
        chat_history.append_message(self.username, {"dir": "out", "to": to, "msg": text, "time": now_str()})

    def request_online(self):
        self._send_raw({"type": "list_request"})

    def _recv_loop(self):
        try:
            while self.running:
                data = self.sock.recv(4096).decode('utf-8')
                if not data:
                    break
                self._recv_buffer += data
                while DELIM in self._recv_buffer:
                    raw, self._recv_buffer = self._recv_buffer.split(DELIM, 1)
                    try:
                        obj = json.loads(raw)
                    except Exception:
                        continue
                    # push to queue for consumer
                    self.recv_queue.put(obj)
                    # automatically save message type 'message' to history (incoming)
                    if obj.get('type') == 'message':
                        chat_history.append_message(self.username, {"dir": "in", "from": obj.get('from'), "to": obj.get('to'), "msg": obj.get('msg'), "time": obj.get('time')})
        except Exception:
            pass
        finally:
            self.running = False
            try:
                self.sock.close()
            except:
                pass

    def close(self):
        self.running = False
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
        except:
            pass
        try:
            self.sock.close()
        except:
            pass

# ---------------- CLI runner ----------------
def cli_main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', default=5555, type=int)
    args = parser.parse_args()

    name = input("Nhập tên của bạn: ").strip()
    if not name:
        print("Tên không hợp lệ.")
        return
    client = ChatClient(name, host=args.host, port=args.port)
    client.connect()
    print("Đã kết nối. Gõ '/help' để biết lệnh.")
    # print history
    hist = chat_history.load_history(name, limit=200)
    if hist:
        print("---- Lịch sử ----")
        for h in hist:
            if h.get('dir') == 'in':
                print(f"[{h.get('time')}] {h.get('from')} -> {h.get('to')}: {h.get('msg')}")
            else:
                print(f"[{h.get('time')}] me -> {h.get('to')}: {h.get('msg')}")
        print("---- Kết thúc lịch sử ----")

    def consumer_loop():
        while client.running:
            try:
                obj = client.recv_queue.get(timeout=0.5)
            except Empty:
                continue
            t = obj.get('type')
            if t == 'message':
                print(f"[{obj.get('time')}] {obj.get('from')} -> {obj.get('to')}: {obj.get('msg')}")
            elif t == 'system':
                print(f"[{obj.get('time')}] *SYSTEM* {obj.get('msg')}")
            elif t == 'online_list':
                print(f"*ONLINE*: {', '.join(obj.get('users', []))}")
            elif t == 'join_ack':
                if not obj.get('ok'):
                    print("Join failed:", obj.get('reason'))
                    client.close()
                    return
                else:
                    print(f"Welcome! Joined at {obj.get('time')}")
            else:
                print("RAW:", obj)

    cons_t = threading.Thread(target=consumer_loop, daemon=True)
    cons_t.start()

    try:
        while client.running:
            text = input()
            if not text:
                continue
            if text.lower() in ('/quit', '/exit'):
                break
            if text.startswith('/w '):
                # private: /w Bob hello
                parts = text.split(' ', 2)
                if len(parts) >= 3:
                    _, target, body = parts
                    client.send_message(body, to=target)
                else:
                    print("Usage: /w <username> <message>")
            elif text == '/online':
                client.request_online()
            elif text == '/history':
                hist = chat_history.load_history(client.username, limit=200)
                for h in hist:
                    if h.get('dir') == 'in':
                        print(f"[{h.get('time')}] {h.get('from')} -> {h.get('to')}: {h.get('msg')}")
                    else:
                        print(f"[{h.get('time')}] me -> {h.get('to')}: {h.get('msg')}")
            elif text == '/help':
                print("Commands:\n  /w <user> <msg>  (private)\n  /online  (show online)\n  /history (show local history)\n  /quit")
            else:
                client.send_message(text, to='all')
    finally:
        client.close()
        print("Đã thoát.")

if __name__ == "__main__":
    cli_main()
