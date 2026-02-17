🛒 MiniMart – Dockerized Full-Stack E-Commerce Application

MiniMart is a containerised full-stack e-commerce web application built using Flask, PostgreSQL, Nginx, and Docker Compose.

This project demonstrates practical DevOps fundamentals including multi-container orchestration, service networking, persistent storage, and API-driven architecture.

🚀 Architecture Overview

The application follows a clean multi-container design:

Frontend (Nginx)
        ↓
Backend (Flask REST API)
        ↓
Database (PostgreSQL)

Services

Frontend – Nginx container serving static HTML/CSS/JavaScript

Backend – Flask REST API handling business logic

Database – PostgreSQL container with persistent volume

Docker Network – Enables inter-service communication

Named Volume – Ensures database data persists across restarts

🛠 Tech Stack

Python 3.11

Flask

Flask-SQLAlchemy

PostgreSQL 16

Nginx (Alpine)

Docker

Docker Compose

REST API Architecture

📦 Features
🛍 Product Management

List all products

Add new products (Admin section)

Persistent storage in PostgreSQL

🛒 Cart System

Add items to cart

View cart contents

Calculate totals dynamically

💳 Checkout

Convert cart into an order

Order stored in database

Cart cleared after checkout

🩺 Health Monitoring

/health endpoint for backend status check

🧠 DevOps Concepts Demonstrated

Multi-container orchestration with Docker Compose

Service-to-service networking via Docker bridge network

Environment variable configuration

Volume-based persistent database storage

Port publishing and host binding

Container debugging & log inspection

Git workflow and GitHub integration

OAuth authentication handling for Git push

📂 Project Structure
minimart-docker/
│
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   └── index.html
│
├── docker-compose.yml
├── .gitignore
└── README.md

▶️ How to Run the Project
1️⃣ Clone the Repository
git clone https://github.com/teeblack7/minimart-docker.git
cd minimart-docker

2️⃣ Build and Start Containers
docker compose up -d --build

3️⃣ Access the Application

Frontend:
👉 http://localhost:8090
 (or configured port)

Backend Health Check:
👉 http://localhost:5050/health

🗄 Database Persistence

The PostgreSQL service uses a named Docker volume:

pgdata


This ensures data remains intact even if containers are stopped or rebuilt.

🔍 API Endpoints
Method	Endpoint	Description
GET	/health	Backend status
GET	/api/products	List products
POST	/api/products	Add product
GET	/api/cart	View cart
POST	/api/cart	Add to cart
POST	/api/checkout	Checkout order
🎯 Learning Objectives Achieved

This project was built to demonstrate:

Designing a containerised full-stack application

Implementing RESTful backend architecture

Managing persistent storage with Docker volumes

Debugging networking and port conflicts in WSL/Docker Desktop

Applying Git version control and pushing to GitHub

Handling authentication via OAuth during Git operations

🚀 Future Improvements

Replace Flask development server with Gunicorn (production-ready)

Add Redis for cart session storage

Implement JWT authentication

Add CI/CD with GitHub Actions

Deploy to a cloud provider (AWS / Render / Railway)

Add monitoring stack (Prometheus + Grafana)

👤 Author

Olatunji Babatunde
DevOps & Full-Stack Enthusiast
GitHub: https://github.com/teeblack7

💼 Portfolio Value

This project demonstrates hands-on experience with:

Containerisation

Backend API design

Database management

DevOps fundamentals

Real-world debugging and deployment workflows

If you'd like, I can now:

🔥 Rewrite this for a CV project description (2–3 lines)

🔥 Create a LinkedIn-ready project post

🔥 Add a professional architecture diagram

🔥 Upgrade it to a production-ready deployment guide**

You're officially building a strong DevOps portfolio 🚀
