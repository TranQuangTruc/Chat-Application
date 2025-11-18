import socket
import threading
import json

HOST = '127.0.0.1'
PORT = 65432

def receive_messages(sock):
    while True:
        try:
            data = sock.recv(4096)
            if not data:
                print("Server disconnected.")
                break
            # server gửi JSON; parse rồi in
            try:
                msg = json.loads(data.decode())
                mtype = msg.get('type')
                if mtype == 'system':
                    print(f"[SYSTEM] {msg.get('msg')}")
                elif mtype == 'chat':
                    print(f"{msg.get('from')}: {msg.get('msg')}")
                elif mtype == 'private':
                    print(f"[PRIVATE] {msg.get('from')}: {msg.get('msg')}")
                elif mtype == 'user_list':
                    print("Online:", ", ".join(msg.get('users', [])))
                else:
                    print(data.decode())
            except Exception:
                print(data.decode())
        except:
            print("Connection closed.")
            break


def main():
    username = input("Enter username: ").strip()
    if not username:
        print("Username required")
        return

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(json.dumps({"username": username}).encode())
        threading.Thread(target=receive_messages, args=(s,), daemon=True).start()

        print("Connected to chat! Type messages. Use /w <user> <msg> for private message. Type exit to quit.")
        while True:
            msg = input()
            if not msg:
                continue
            if msg.lower() == "exit":
                break
            if msg.startswith("/w "):
                try:
                    _, to, rest = msg.split(' ', 2)
                    payload = {"type": "chat_private", "to": to, "msg": rest}
                except ValueError:
                    print("Usage: /w <user> <message>")
                    continue
            else:
                payload = {"type": "chat_all", "msg": msg}

            try:
                s.sendall(json.dumps(payload).encode())
            except Exception:
                print("Failed to send message.")
                break


if __name__ == "__main__":
    main()