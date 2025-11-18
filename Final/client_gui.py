import socket
import threading
import tkinter as tk
from tkinter import messagebox, simpledialog, scrolledtext
import json

HOST = '127.0.0.1'
PORT = 65432

class ChatClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Messenger Mini")
        self.root.geometry("800x520")
        self.root.configure(bg="#f5f6fa")

        self.sock = None
        self.username = None
        self.current_target = "all"

        self.build_ui()
        self.connect_to_server()

    def build_ui(self):
        # Left: danh sách users
        left = tk.Frame(self.root, bg="#ffffff", width=220)
        left.pack(side=tk.LEFT, fill=tk.Y)
        left.pack_propagate(False)

        lbl_title = tk.Label(left, text="Contacts", bg="#ffffff", font=("Helvetica", 14, "bold"))
        lbl_title.pack(pady=(12,6))

        self.list_users = tk.Listbox(left, activestyle='none', bd=0, highlightthickness=0, font=("Helvetica", 11))
        self.list_users.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=(0,10))
        self.list_users.bind("<<ListboxSelect>>", self.select_user)

        # Right: khung chat
        right = tk.Frame(self.root, bg="#f5f6fa")
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        header = tk.Frame(right, bg="#f5f6fa")
        header.pack(fill=tk.X, padx=10, pady=10)

        self.lbl_chat_with = tk.Label(header, text="Chat (All)", font=("Helvetica", 13, "bold"), bg="#f5f6fa")
        self.lbl_chat_with.pack(side=tk.LEFT)

        # Text area
        self.text_area = scrolledtext.ScrolledText(right, wrap=tk.WORD, state='disabled', font=("Helvetica", 11), bg="#ffffff", bd=0, padx=10, pady=10)
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=10)
        self.text_area.tag_config('me', foreground='#0b93f6', justify='right')
        self.text_area.tag_config('other', foreground='#222222', justify='left')
        self.text_area.tag_config('system', foreground='#888888', justify='center')

        # Input area
        bottom = tk.Frame(right, bg="#f5f6fa")
        bottom.pack(fill=tk.X, padx=10, pady=10)

        self.entry_message = tk.Entry(bottom, font=("Helvetica", 12))
        self.entry_message.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=(0,8))
        self.entry_message.bind("<Return>", self.send_message)

        self.btn_send = tk.Button(bottom, text="Send", width=10, command=self.send_message, bg="#0b93f6", fg="#ffffff", bd=0, font=("Helvetica", 11, "bold"))
        self.btn_send.pack(side=tk.RIGHT)

    def connect_to_server(self):
        self.username = simpledialog.askstring("Username", "Enter your name:", parent=self.root)
        if not self.username:
            self.root.destroy()
            return

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((HOST, PORT))
            self.sock.sendall(json.dumps({"username": self.username}).encode())
            threading.Thread(target=self.receive_messages, daemon=True).start()
            # Không tự add message ở đây — server sẽ gửi lại chat để đồng bộ
            self.display_message(f"[SYSTEM] Connected as {self.username}", tag='system')
        except Exception as e:
            messagebox.showerror("Connection Error", f"Cannot connect to server:\n{e}")
            self.root.destroy()

    def receive_messages(self):
        while True:
            try:
                data = self.sock.recv(4096)
                if not data:
                    self.display_message("[SYSTEM] Disconnected from server.", tag='system')
                    break
                # Có thể nhận nhiều lần, nhưng server gửi JSON từng tin
                msg = json.loads(data.decode())
                self.handle_message(msg)
            except Exception:
                break

    def handle_message(self, msg):
        mtype = msg.get("type")
        if mtype == "system":
            self.display_message(f"[SYSTEM] {msg.get('msg')}", tag='system')
        elif mtype == "chat":
            sender = msg.get('from')
            text = msg.get('msg')
            tag = 'me' if sender == self.username else 'other'
            self.display_message(f"{sender}: {text}", tag=tag)
        elif mtype == "private":
            sender = msg.get('from')
            text = msg.get('msg')
            tag = 'me' if sender == self.username else 'other'
            self.display_message(f"[PRIVATE] {sender}: {text}", tag=tag)
        elif mtype == "user_list":
            self.update_user_list(msg.get('users', []))

    def update_user_list(self, users):
        self.list_users.delete(0, tk.END)
        self.list_users.insert(tk.END, "All")
        for u in users:
            if u != self.username:
                self.list_users.insert(tk.END, u)

    def select_user(self, event):
        selected = self.list_users.curselection()
        if selected:
            val = self.list_users.get(selected[0])
            if val == "All":
                self.current_target = "all"
                self.lbl_chat_with.config(text="Chat (All)")
            else:
                self.current_target = val
                self.lbl_chat_with.config(text=f"Chat with {val}")
        else:
            self.current_target = "all"
            self.lbl_chat_with.config(text="Chat (All)")

    def send_message(self, event=None):
        text = self.entry_message.get().strip()
        if not text:
            return

        if self.current_target == "all":
            payload = {"type": "chat_all", "msg": text}
        else:
            payload = {"type": "chat_private", "to": self.current_target, "msg": text}

        try:
            self.sock.sendall(json.dumps(payload).encode())
            self.entry_message.delete(0, tk.END)
            # Không gọi display_message tại đây để tránh duplicate — server sẽ echo lại
        except Exception:
            self.display_message("[SYSTEM] Cannot send message. Connection lost.", tag='system')

    def display_message(self, msg, tag='other'):
        self.text_area.config(state='normal')
        # mỗi message trên 1 dòng, thêm tag để style
        self.text_area.insert(tk.END, msg + "\n", tag)
        self.text_area.config(state='disabled')
        self.text_area.yview(tk.END)

    def on_close(self):
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ChatClient(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()