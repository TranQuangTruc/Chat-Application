// server_phan1.js
// -----------------------------------------------
// PHAN 1: KHOI TAO SERVER + LOG + MIDDLEWARE TU VIET
// -----------------------------------------------

const express = require('express')
const http = require('http')
const { Server } = require('socket.io')

const app = express()
const server = http.createServer(app)
const io = new Server(server, {
    cors: { origin: "*" }
})

// Danh sách người dùng: id => thông tin
const users = {}

// Lịch sử tin nhắn lưu tạm (tối đa 50 tin)
let messageHistory = []

// Middleware custom cho logging
io.use((socket, next) => {
    console.log(`🔗 [MIDDLEWARE] Socket ${socket.id} đang yêu cầu kết nối...`)
    next()
})

io.on('connection', (socket) => {
    console.log(`🟢 [CONNECT] ${socket.id} đã kết nối`)

    // Tạo username tạm cho client
    users[socket.id] = {
        id: socket.id,
        username: `NguoiDung_${socket.id.slice(0, 4)}`,
        room: "global"
    }

    console.log(`   ➜ Tạo username: ${users[socket.id].username}`)

    // Khi client ngắt kết nối
    socket.on('disconnect', () => {
        console.log(`🔴 [DISCONNECT] ${users[socket.id]?.username} đã rời`)
        delete users[socket.id]
    })
})

server.listen(3000, () => {
    console.log("🚀 Server phần 1 chạy tại cổng 3000")
})
