# VectorVault 🚀

**VectorVault is not a "Chat with your PDF" app. It is the production-ready, secure, and asynchronous backend platform designed to power *any* number of RAG (Retrieval-Augmented Generation) applications.**

This project is a backend-first, multi-tenant API platform that demonstrates a complete professional-grade system. It combines three in-demand skill sets:

* **🛡️ Backend Engineering:** A secure, multi-tenant API with JWT authentication, user isolation, and robust database management with Alembic migrations.
* **🤖 MLOps:** A complete, asynchronous RAG pipeline to process, embed, and query documents in a vector database (ChromaDB).
* **⚙️ DevOps:** A fully containerized 5-service application orchestrated with Docker Compose, complete with automated CI testing via GitHub Actions.

[![VectorVault CI](https://github.com/YOUR_USERNAME/VectorVault/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/VectorVault/actions/workflows/ci.yml)

## 🏛️ System Architecture

This project runs as a 5-service application orchestrated by Docker Compose. The `api` service automatically runs database migrations on startup to ensure the schema is always up-to-date before starting the server.



1.  **FastAPI (API):** The main API server, handling user requests, authentication, and dispatching tasks.
2.  **PostgreSQL (DB):** The primary SQL database for storing user accounts, knowledge bases, and document metadata.
3.  **Redis (Broker):** The message broker that holds background jobs (like "process this PDF") for Celery.
4.  **Celery (Worker):** A background worker that consumes jobs from Redis. It handles all the slow, heavy tasks (parsing, chunking, embedding) so the API can respond instantly.
5.  **ChromaDB (Vector DB):** The vector database that stores the document embeddings for fast semantic search.

## ✨ Features

* **Secure Authentication:** Full user registration and login via JWT (OAuth2) tokens.
* **Multi-Tenant Data Isolation:** All uploaded documents and queries are 100% isolated to the authenticated user.
* **Asynchronous Document Processing:** PDF uploads are non-blocking. The API instantly returns a task ID, while a Celery worker processes the file in the background.
* **Database Migrations:** Uses Alembic to professionally manage all database schema changes.
* **Automated CI Pipeline:** Includes a GitHub Actions workflow that automatically:
    1.  Spins up all 5 services (Postgres, Redis, etc.)
    2.  Runs Alembic migrations.
    3.  Runs the full `pytest` suite against the live API.

## 🛠️ Technology Stack

| Category | Technology |
| :--- | :--- |
| **Backend** | FastAPI, Pydantic, Uvicorn |
| **Database** | PostgreSQL |
| **Vector Database** | ChromaDB |
| **Task Queue** | Celery, Redis |
| **ORM & Migrations** | SQLAlchemy, Alembic |
| **Authentication** | `python-jose` (JWT), `passlib` (bcrypt) |
| **DevOps** | Docker, Docker Compose |
| **Testing** | Pytest, HTTPX |
| **CI/CD** | GitHub Actions |

## 🚀 Getting Started (Local Development)

This entire 5-service application can be built and run with a single command.

### Prerequisites

* Docker
* Docker Compose

### 1. Clone the Repository

```bash
git clone [https://github.com/YOUR_USERNAME/VectorVault.git](https://github.com/YOUR_USERNAME/VectorVault.git)
cd VectorVault
