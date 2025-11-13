const express = require('express')
const http = require('http')
const { Server } = require('socket.io')

const app = express()
const server = http.createServer(app)
const io = new Server(server)

const users = {} // Lưu danh sách người dùng theo socket.id

io.on('connection', (socket) => {
  console.log('🟢 Người dùng mới kết nối:', socket.id)

  // Tạo tên tạm thời cho người dùng
  users[socket.id] = `NguoiDung_${socket.id.slice(0, 4)}`
  console.log(`${users[socket.id]} đã tham gia`)

  socket.on('disconnect', () => {
    console.log(`🔴 ${users[socket.id]} đã rời khỏi`)
    delete users[socket.id]
  })
})

server.listen(3000, () => console.log(' Server đang chạy tại cổng 3000'))
