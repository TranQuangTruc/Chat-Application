import socket
import threading
import json

HOST = '127.0.0.1'
PORT = 65432

clients = {}  # username -> conn
lock = threading.Lock()


def broadcast(message, exclude=None):
    """Gửi message đến tất cả client. Nếu exclude != None thì sẽ bỏ user đó."""
    with lock:
        for user, conn in list(clients.items()):
            if user == exclude:
                continue
            try:
                conn.sendall(json.dumps(message).encode())
            except Exception:
                try:
                    conn.close()
                except:
                    pass
                del clients[user]


def update_user_list():
    """Gửi danh sách người online cho tất cả client."""
    with lock:
        user_list = list(clients.keys())
    msg = {"type": "user_list", "users": user_list}
    broadcast(msg)


def handle_client(conn):
    username = None
    try:
        data = conn.recv(1024).decode()
        info = json.loads(data)
        username = info.get("username")

        if not username:
            conn.sendall(json.dumps({"type": "system", "msg": "Invalid username."}).encode())
            conn.close()
            return

        with lock:
            if username in clients:
                conn.sendall(json.dumps({"type": "system", "msg": "Username already taken!"}).encode())
                conn.close()
                return
            clients[username] = conn

        # Thông báo cho mọi người (trừ người mới) rằng có người tham gia
        broadcast({"type": "system", "msg": f"{username} has joined the chat!"}, exclude=username)
        update_user_list()

        while True:
            data = conn.recv(2048)
            if not data:
                break
            msg = json.loads(data.decode())
            msg_type = msg.get("type")

            if msg_type == "chat_all":
                text = msg.get("msg", "")
                # Gửi cho tất cả (bao gồm cả người gửi) để đảm bảo sender cũng thấy tin
                broadcast({"type": "chat", "from": username, "msg": text}, exclude=None)
            elif msg_type == "chat_private":
                target = msg.get("to")
                text = msg.get("msg", "")
                with lock:
                    target_conn = clients.get(target)
                if target_conn:
                    try:
                        target_conn.sendall(json.dumps({"type": "private", "from": username, "msg": text}).encode())
                        # gửi lại cho chính mình để hiển thị (nếu muốn duplicate không xảy ra vì server chỉ gửi 1 lần back)
                        conn.sendall(json.dumps({"type": "private", "from": username, "msg": text}).encode())
                    except Exception:
                        conn.sendall(json.dumps({"type": "system", "msg": f"Failed to deliver to {target}."}).encode())
                else:
                    conn.sendall(json.dumps({"type": "system", "msg": f"User {target} not found!"}).encode())
    except Exception:
        pass
    finally:
        with lock:
            if username and username in clients:
                del clients[username]
        if username:
            broadcast({"type": "system", "msg": f"{username} has left the chat!"})
            update_user_list()
        try:
            conn.close()
        except:
            pass


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"[SERVER STARTED] Listening on {HOST}:{PORT}")

        while True:
            conn, _ = s.accept()
            threading.Thread(target=handle_client, args=(conn,), daemon=True).start()


if __name__ == "__main__":
    main()