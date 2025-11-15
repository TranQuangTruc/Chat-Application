# chat_history.py
import json
import os
from datetime import datetime

HISTORY_DIR = "chat_history"

def ensure_history_dir():
    """Đảm bảo thư mục lịch sử tồn tại"""
    if not os.path.exists(HISTORY_DIR):
        os.makedirs(HISTORY_DIR)

def get_user_file(username):
    """Lấy đường dẫn file lịch sử của user"""
    # Làm sạch username để tránh lỗi đường dẫn
    safe_username = "".join(c for c in username if c.isalnum() or c in ('-', '_')).rstrip()
    if not safe_username:
        safe_username = "unknown"
    return os.path.join(HISTORY_DIR, f"{safe_username}.json")

def repair_history_file(username):
    """Sửa chữa file lịch sử bị hỏng"""
    ensure_history_dir()
    user_file = get_user_file(username)
    
    if not os.path.exists(user_file):
        return True
        
    try:
        with open(user_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            
        if not content:
            return True
            
        # Thử parse JSON
        json.loads(content)
        return True  # File OK
        
    except json.JSONDecodeError:
        # File hỏng, tạo file mới
        try:
            backup_file = user_file + ".backup_" + datetime.now().strftime('%Y%m%d_%H%M%S')
            os.rename(user_file, backup_file)
            print(f"Đã sửa file lịch sử hỏng, backup: {backup_file}")
            return True
        except Exception as e:
            print(f" Không thể sửa file lịch sử: {e}")
            return False

def append_message(username, message_data):
    """
    Thêm tin nhắn vào lịch sử
    
    Args:
        username: Tên người dùng
        message_data: Dict chứa thông tin tin nhắn
            - dir: 'in' (nhận) hoặc 'out' (gửi)
            - from: Người gửi (với tin nhắn đến)
            - to: Người nhận hoặc 'all'
            - msg: Nội dung tin nhắn
            - time: Thời gian
    """
    ensure_history_dir()
    
    # Kiểm tra và sửa file nếu cần
    if not repair_history_file(username):
        return False
        
    user_file = get_user_file(username)
    
    try:
        # Đọc lịch sử hiện tại
        history = []
        if os.path.exists(user_file):
            try:
                with open(user_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        history = json.loads(content)
            except json.JSONDecodeError as e:
                print(f" File lịch sử bị lỗi, tạo file mới: {e}")
                # Tạo file mới
                history = []
        
        # Thêm tin nhắn mới
        history.append(message_data)
        
        # Giới hạn lịch sử (1000 tin nhắn gần nhất)
        if len(history) > 1000:
            history = history[-1000:]
        
        # Lưu file
        with open(user_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
            
        return True
        
    except Exception as e:
        print(f" Lỗi lưu lịch sử: {e}")
        return False

def load_history(username, limit=200):
    """
    Đọc lịch sử tin nhắn
    
    Args:
        username: Tên người dùng
        limit: Số tin nhắn tối đa (0 để lấy tất cả)
    
    Returns:
        List các tin nhắn (mới nhất đầu tiên)
    """
    ensure_history_dir()
    user_file = get_user_file(username)
    
    try:
        if os.path.exists(user_file):
            with open(user_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    return []
                
                try:
                    history = json.loads(content)
                except json.JSONDecodeError as e:
                    print(f"⚠️ File lịch sử bị lỗi, tạo file mới: {e}")
                    # Sao lưu file hỏng và tạo file mới
                    backup_file = user_file + ".backup"
                    try:
                        os.rename(user_file, backup_file)
                        print(f" Đã sao lưu file hỏng thành: {backup_file}")
                    except:
                        pass
                    return []
            
            # Đảo ngược để tin nhắn mới nhất ở cuối
            history.reverse()
            
            if limit and limit > 0:
                return history[:limit]
            return history
            
    except Exception as e:
        print(f" Lỗi đọc lịch sử: {e}")
    
    return []

def clear_history(username):
    """Xóa toàn bộ lịch sử của user"""
    ensure_history_dir()
    user_file = get_user_file(username)
    
    try:
        if os.path.exists(user_file):
            os.remove(user_file)
            return True
    except Exception as e:
        print(f" Lỗi xóa lịch sử: {e}")
    
    return False

def get_history_stats(username):
    """Lấy thống kê lịch sử"""
    history = load_history(username, limit=0)
    
    total = len(history)
    incoming = len([h for h in history if h.get('dir') == 'in'])
    outgoing = len([h for h in history if h.get('dir') == 'out'])
    
    return {
        "total_messages": total,
        "incoming": incoming,
        "outgoing": outgoing
    }

# Test code
if __name__ == "__main__":
    # Test các chức năng
    test_user = "test_user"
    
    # Thêm tin nhắn test
    append_message(test_user, {
        "dir": "out",
        "to": "all", 
        "msg": "Xin chào mọi người!",
        "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    
    append_message(test_user, {
        "dir": "in",
        "from": "user2",
        "to": "test_user",
        "msg": "Chào bạn!",
        "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    
    # Đọc lịch sử
    history = load_history(test_user)
    print(f" Lịch sử cho {test_user}: {len(history)} tin nhắn")
    
    # Thống kê
    stats = get_history_stats(test_user)
    print(f" Thống kê: {stats}")