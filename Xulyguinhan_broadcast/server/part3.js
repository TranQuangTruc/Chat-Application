// server_phan3.js
// -----------------------------------------------
// PHAN 3: BROADCAST + ROOM + TYPING
// -----------------------------------------------

const express = require('express')
const http = require('http')
const { Server } = require('socket.io')

const app = express()
const server = http.createServer(app)
const io = new Server(server)

const users = {}

io.on('connection', (socket) => {

    users[socket.id] = {
        username: `NguoiDung_${socket.id.slice(0, 4)}`,
        room: "global"
    }

    socket.join("global")

    socket.on("gui-tin-nhan", (text) => {
        const msg = {
            nguoiGui: users[socket.id].username,
            noidung: text,
            room: users[socket.id].room,
            time: new Date().toLocaleTimeString()
        }

        // broadcast đến đúng room
        io.to(users[socket.id].room).emit("nhan-tin-nhan", msg)
    })

    // Khi người dùng đang nhập
    socket.on("dang-nhap-tin", () => {
        socket.to(users[socket.id].room).emit("typing", users[socket.id].username)
    })

    // Đổi phòng chat
    socket.on("join-room", (roomName) => {
        socket.leave(users[socket.id].room)
        users[socket.id].room = roomName
        socket.join(roomName)

        socket.emit("thong-bao", `Bạn đã vào phòng ${roomName}`)
    })
})

server.listen(3000, () => console.log("🚀 Server phần 3 chạy tại cổng 3000"))
