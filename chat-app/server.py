#!/usr/bin/env python3
# server.py
# Run: python server.py

import socket
import threading
import json
from datetime import datetime

HOST = '0.0.0.0'
PORT = 5555
DELIM = '\n'  # use newline as message delimiter

clients_lock = threading.Lock()
clients = {}  # username -> (conn, addr)

def now_str():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def send_json(conn, obj):
    try:
        data = json.dumps(obj, ensure_ascii=False) + DELIM
        conn.sendall(data.encode('utf-8'))
    except Exception:
        # caller will handle removal
        pass

def broadcast(obj, exclude_username=None):
    with clients_lock:
        for user, (conn, addr) in list(clients.items()):
            if user == exclude_username:
                continue
            send_json(conn, obj)

def handle_connection(conn, addr):
    buffer = ''
    username = None
    try:
        # Expect initial message to be a "join" with username
        while True:
            chunk = conn.recv(4096).decode('utf-8')
            if not chunk:
                raise ConnectionResetError()
            buffer += chunk
            while DELIM in buffer:
                raw, buffer = buffer.split(DELIM, 1)
                try:
                    msg = json.loads(raw)
                except Exception:
                    continue
                if msg.get('type') == 'join':
                    requested = msg.get('from')
                    if not requested:
                        send_json(conn, {"type": "error", "msg": "No username provided"})
                        conn.close()
                        return
                    with clients_lock:
                        if requested in clients:
                            send_json(conn, {"type": "join_ack", "ok": False, "reason": "username_taken"})
                            conn.close()
                            return
                        username = requested
                        clients[username] = (conn, addr)
                    # ack join
                    send_json(conn, {"type": "join_ack", "ok": True, "time": now_str()})
                    # notify others
                    broadcast({"type": "system", "msg": f"{username} joined", "time": now_str()}, exclude_username=username)
                    # send current online list
                    with clients_lock:
                        online = list(clients.keys())
                    send_json(conn, {"type": "online_list", "users": online})
                    break
                else:
                    # ignore until join
                    continue
            if username:
                break

        # main loop: receive messages
        while True:
            chunk = conn.recv(4096).decode('utf-8')
            if not chunk:
                raise ConnectionResetError()
            buffer += chunk
            while DELIM in buffer:
                raw, buffer = buffer.split(DELIM, 1)
                try:
                    msg = json.loads(raw)
                except Exception:
                    continue
                mtype = msg.get('type')
                if mtype == 'message':
                    to = msg.get('to', 'all')
                    msg_out = {
                        "type": "message",
                        "from": username,
                        "to": to,
                        "msg": msg.get('msg'),
                        "time": now_str()
                    }
                    if to == 'all':
                        broadcast(msg_out, exclude_username=None)
                    else:
                        # private: send to recipient and echo to sender
                        with clients_lock:
                            target = clients.get(to)
                            sender = clients.get(username)
                        if target:
                            send_json(target[0], msg_out)
                        # echo back to sender
                        send_json(conn, msg_out)
                elif mtype == 'list_request':
                    with clients_lock:
                        online = list(clients.keys())
                    send_json(conn, {"type": "online_list", "users": online})
                else:
                    # unknown type: ignore or send error
                    send_json(conn, {"type": "error", "msg": "unknown_type"})
    except (ConnectionResetError, ConnectionAbortedError):
        pass
    finally:
        # clean up
        if username:
            with clients_lock:
                try:
                    del clients[username]
                except KeyError:
                    pass
            broadcast({"type": "system", "msg": f"{username} left", "time": now_str()})
        try:
            conn.close()
        except:
            pass
        print(f"[DISCONNECTED] {addr} ({username})")

def main():
    print(f"Starting chat server on {HOST}:{PORT}")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(100)
    try:
        while True:
            conn, addr = s.accept()
            print(f"[NEW CONNECTION] {addr}")
            t = threading.Thread(target=handle_connection, args=(conn, addr), daemon=True)
            t.start()
    except KeyboardInterrupt:
        print("Shutting down server...")
    finally:
        s.close()

if __name__ == "__main__":
    main()
