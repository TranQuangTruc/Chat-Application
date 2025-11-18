// server_phan5.js
// ----------------------------------------------------
// PHAN 5: NHAN RIENG + RATE LIMIT + ERROR HANDLER
// ----------------------------------------------------

const express = require('express')
const http = require('http')
const { Server } = require('socket.io')

const app = express()
const server = http.createServer(app)
const io = new Server(server)

const users = {}

// Rate limit chống spam
const messageLimit = {}
const RATE_MAX = 5      // 5 tin/giây
const RATE_WINDOW = 1000

io.on('connection', (socket) => {

    users[socket.id] = `NguoiDung_${socket.id.slice(0, 4)}`

    messageLimit[socket.id] = []

    // CHAT RIÊNG
    socket.on("gui-rieng", ({ den, noidung }) => {

        const idNhan = Object.keys(users)
            .find(id => users[id] === den)

        if (!idNhan) {
            socket.emit("loi", "Không tìm thấy người nhận")
            return
        }

        const msg = {
            loai: "rieng",
            nguoiGui: users[socket.id],
            noidung,
            time: new Date().toLocaleTimeString()
        }

        console.log(`📩 [DM] ${users[socket.id]} → ${den}: ${noidung}`)

        io.to(idNhan).emit("nhan-tin-nhan", msg)
        socket.emit("nhan-tin-nhan", msg)
    })

    // Rate limit gửi tin
    socket.on("gui-tin-nhan", (text) => {

        const now = Date.now()
        messageLimit[socket.id] = messageLimit[socket.id].filter(t => now - t < RATE_WINDOW)

        if (messageLimit[socket.id].length >= RATE_MAX) {
            return socket.emit("loi", "Bạn gửi quá nhanh, hãy chậm lại")
        }

        messageLimit[socket.id].push(now)

        const msg = {
            loai: "cong-khai",
            nguoiGui: users[socket.id],
            noidung: text,
            time: new Date().toLocaleTimeString()
        }

        io.emit("nhan-tin-nhan", msg)
    })

    socket.on('disconnect', () => {
        console.log(`🔴 ${users[socket.id]} đã rời`)
        delete users[socket.id]
    })
})

server.listen(3000, () => console.log("🚀 Server phần 5 chạy tại cổng 3000"))
