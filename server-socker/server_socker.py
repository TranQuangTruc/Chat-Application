import socket
import threading

# Danh sách lưu trữ tất cả các client kết nối
clients = []

# Thiết lập server
HOST = '127.0.0.1'  # localhost
PORT = 12345        # cổng server

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
print(f"Server đang chạy tại {HOST}:{PORT}")

# Hàm gửi thông điệp đến tất cả client (broadcast)
def broadcast(message, sender=None):
    for client in clients:
        # Không gửi lại cho client gửi tin
        if client != sender:
            try:
                client.send(message)
            except:
                clients.remove(client)

# Hàm xử lý từng client
def handle_client(client, address):
    print(f"[KẾT NỐI] {address} đã kết nối.")
    while True:
        try:
            message = client.recv(1024)
            if message:
                print(f"[{address}] {message.decode()}")
                broadcast(message, client)  # gửi message cho tất cả client khác
            else:
                raise Exception("Client đã ngắt kết nối")
        except:
            print(f"[NGẮT KẾT NỐI] {address}")
            clients.remove(client)
            client.close()
            break

# Hàm chấp nhận kết nối client mới
def accept_clients():
    while True:
        client, address = server.accept()
        clients.append(client)
        thread = threading.Thread(target=handle_client, args=(client, address))
        thread.start()

accept_thread = threading.Thread(target=accept_clients)
accept_thread.start()
