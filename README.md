# 📚 CollabLearn – Collaborative Study Platform

[![CI](https://github.com/Henokgeta12/CollabLearn/actions/workflows/ci.yml/badge.svg)](https://github.com/Henokgeta12/CollabLearn/actions)
![GitHub repo size](https://img.shields.io/github/repo-size/Henokgeta12/CollabLearn?style=flat-square)
![GitHub stars](https://img.shields.io/github/stars/Henokgeta12/CollabLearn?color=yellow)
![GitHub last commit](https://img.shields.io/github/last-commit/Henokgeta12/CollabLearn?style=flat-square)
![GitHub License](https://img.shields.io/github/license/Henokgeta12/CollabLearn?color=green)

Welcome to **CollabLearn**, a web application designed to facilitate collaborative learning among students. This platform enables users to create or join study groups, communicate in real-time, and share resources such as notes and files.

> 🚧 **Note:** This project is currently in its **Minimum Viable Product (MVP)** stage. Feedback is welcome as we iterate toward a full-featured product!

---

## 📸 Demo Preview

<img src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExaGlyMGdpaTl4bm9rcTd2ZGU5M3czc2Jxb3Y0cncyN3YzdGlxaDJ6ZyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/PlZrLrhdzL3K3G0z63/giphy.gif" alt="CollabLearn demo gif" width="100%" />

---

## ✨ Features

- ✅ **User Registration and Authentication** – Secure sign-up/login processes with password hashing to protect user credentials.
- ✉️ **Email Verification** – Upon registration or email update, users receive a verification email to activate their account or confirm changes.
- 🔒 **Password Reset via Email** – Users who forget their password can request a reset link, sent securely to their registered email address.
- 👥 **Study Group Management** – Create, join, and manage groups by topic or project.
- 💬 **Real-Time Messaging** – Built with Socket.IO and Express.js for instant communication within groups.
- 📂 **Resource Sharing** – Upload and manage notes, links, and files for easy collaboration.
- 🙋 **User Profiles** – Personalize your profile with details and preferences.
- 📊 **Activity Analytics** – Track group engagement, resource usage, and communication patterns.

---

## 🛠️ Tech Stack

<div style="display:flex; flex-wrap: wrap; gap: 10px;">
  <img align="left" alt="HTML" width="30px" style="padding-right:10px;" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/html5/html5-plain.svg" />
  <img align="left" alt="CSS" width="30px" style="padding-right:10px;" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/css3/css3-plain.svg" />
  <img align="left" alt="JavaScript" width="30px" style="padding-right:10px;" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/javascript/javascript-original.svg" />
  <img align="left" alt="Python" width="30px" style="padding-right:10px;" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" />
  <img align="left" alt="Flask" width="30px" style="padding-right:10px;" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/flask/flask-original.svg" />
  <img align="left" alt="MySQL" width="30px" style="padding-right:10px;" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/mysql/mysql-original.svg" />
  <img align="left" alt="Node.js" width="30px" style="padding-right:10px;" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/nodejs/nodejs-original.svg" />
  <img align="left" alt="Express" width="30px" style="padding-right:10px;" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/express/express-original.svg" />
  <img align="left" alt="Socket.IO" width="30px" style="padding-right:10px;" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/socketio/socketio-original.svg" />
</div>

<br><br>

---

## ⚙️ Installation

Follow these steps to set up the project locally:

### 1. Clone the Repository
```bash
git clone https://github.com/Henokgeta12/CollabLearn.git
cd CollabLearn

2. Set Up a Virtual Environment
bash
Copy
Edit
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
3. Install Dependencies
bash
Copy
Edit
pip install -r requirements.txt
4. Configure MySQL Database
Make sure MySQL is installed and running.

Create a new database named: collablearn

Update your config.py file with your DB credentials:

SQLALCHEMY_DATABASE_URI = 'mysql://username:password@localhost/collablearn'
5. Apply Migrations
flask db upgrade
6. Run the Flask App

flask run
Visit the app at: http://127.0.0.1:5000/

🚀 Usage
Register an Account – Sign up with your email and password.

Verify Your Email – Check your inbox to activate your account.

Create or Join Groups – Explore or initiate study groups.

Collaborate – Use the real-time chat and share resources within your group.
