const http = require("http");
const express = require("express");
const mysql = require('mysql2');
const cors = require("cors");
const url = require('url');
const { Socket } = require("socket.io");

require('dotenv').config();

const app = express();

app.use(cors());

const server = http.createServer(app);

// Change the second declaration to a different variable name like `socketIo`.
const socketIo = require("socket.io")(server, {
    cors: {
        origin: "*",
        methods: ["GET", "POST"],
        credentials: true,
    }
});

// Function to parse the DATABASE_URL
function parseDatabaseUrl(databaseUrl) {
    const parsedUrl = url.parse(databaseUrl.replace('mysql+pymysql://', 'mysql://'));
    return {
        host: parsedUrl.hostname,
        user: parsedUrl.auth.split(':')[0],
        password: parsedUrl.auth.split(':')[1],
        database: parsedUrl.pathname.slice(1), // Remove leading '/'
    };
}

// Check if DATABASE_URL is set
if (!process.env.DATABASE_URL) {
    console.error('DATABASE_URL environment variable is not set');
    process.exit(1); // Exit the process with an error code
}

const dbConfig = parseDatabaseUrl(process.env.DATABASE_URL);

const db = mysql.createConnection(dbConfig);

db.connect((err) => {
    if (err) {
        console.error('Error connecting to the database:', err);
    } else {
        console.log('Connected to the database');
    }
});

socketIo.on("connection", (socket) => {
    console.log("Client connected");
    socketIo.emit('welcome', 'Welcome to the Collaborative study platform');

    // Remove any existing listeners to prevent duplicates
    socket.removeAllListeners('send_message');

    socket.on('send_message', data => {
        const { group_id, user_id, username, content } = data;

        const query = `INSERT INTO messages (group_id, user_id, content, created_at) VALUES (?, ?, ?, NOW())`;
        const val = [group_id, user_id, content];
        db.query(query, val, (err, result) => {
            if (err) {
                console.error(err);
                return;
            }
        });

        const message = { user: username, content: content, created_at: new Date().toLocaleString() };
        socketIo.emit('chat message', message); 
    });

    socket.on('disconnect', () => {
        console.log('Client disconnected');
    });
});

const port = process.env.PORT || 3000;

server.listen(port, () => {
    console.log('Express chat server running on port 3000');
});
