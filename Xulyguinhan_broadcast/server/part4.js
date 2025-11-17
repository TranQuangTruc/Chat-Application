// server_phan4.js
// -----------------------------------------------
// PHAN 4: THONG BAO VAO/RA + DANH SACH ONLINE + KEEPALIVE
// -----------------------------------------------

const express = require('express')
const http = require('http')
const { Server } = require('socket.io')

const app = express()
const server = http.createServer(app)
const io = new Server(server)

const users = {}

io.on('connection', (socket) => {

    users[socket.id] = `NguoiDung_${socket.id.slice(0, 4)}`

    // Thông báo cho tất cả người khác
    socket.broadcast.emit("thong-bao", `${users[socket.id]} đã vào phòng`)

    // Gửi danh sách người dùng
    io.emit("danh-sach-online", Object.values(users))

    // Ping/pong giữ kết nối
    setInterval(() => {
        socket.emit("ping-check", Date.now())
    }, 5000)

    socket.on("pong-check", (clientTime) => {
        const latency = Date.now() - clientTime
        console.log(`📡 Ping từ ${users[socket.id]} = ${latency}ms`)
    })

    socket.on('disconnect', () => {
        socket.broadcast.emit("thong-bao", `${users[socket.id]} đã rời`)
        delete users[socket.id]
        io.emit("danh-sach-online", Object.values(users))
    })
})

server.listen(3000, () => console.log("🚀 Server phần 4 chạy tại cổng 3000"))
