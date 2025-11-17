// server_phan2.js
// -----------------------------------------------
// PHAN 2: NHAN TIN + KIEM TRA DU LIEU + LUU LICH SU
// -----------------------------------------------

const express = require('express')
const http = require('http')
const { Server } = require('socket.io')

const app = express()
const server = http.createServer(app)
const io = new Server(server)

const users = {}
let messageHistory = []

function validateMessage(text) {
    if (!text || typeof text !== "string") return false
    if (text.trim().length === 0) return false
    if (text.length > 500) return false
    return true
}

io.on('connection', (socket) => {

    users[socket.id] = {
        username: `NguoiDung_${socket.id.slice(0, 4)}`,
        room: "global"
    }

    // Gửi lịch sử tin nhắn cho client mới
    socket.emit("lich-su-tin-nhan", messageHistory)

    socket.on("gui-tin-nhan", (text) => {

        if (!validateMessage(text)) {
            return socket.emit("loi", "Tin nhắn không hợp lệ")
        }

        const msg = {
            id: Date.now(),
            nguoiGui: users[socket.id].username,
            noidung: text,
            thoigian: new Date().toLocaleTimeString(),
            room: users[socket.id].room
        }

        // Lưu lịch sử (tối đa 50 tin)
        messageHistory.push(msg)
        if (messageHistory.length > 50) messageHistory.shift()

        console.log(`💬 [TIN NHAN] ${msg.nguoiGui}: ${msg.noidung}`)
    })
})

server.listen(3000, () => console.log("🚀 Server phần 2 chạy tại cổng 3000"))
