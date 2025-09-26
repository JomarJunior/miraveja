# MiraVeja 🖼️

![MiraVeja Logo](./images/miraveja-logo.png)

---

MiraVeja is an **AI-powered image gallery** designed for exploration, inspiration, and creative workflows.  
It enables users to upload, search, and organize images using **vector embeddings**, integrates with external sources (like DeviantArt), and supports **SSO authentication** out of the box.  

This project is being developed as a **learning-first, open-source platform** — lightweight for a solo developer, but with a design ready for future scaling into a full microservices architecture.

## ✨ Features

- 🔑 **Authentication & SSO**: Keycloak with DeviantArt login (OIDC).  
- 🗂️ **Image Management**: Uploads stored in MinIO, metadata in Postgres.  
- 🔍 **Semantic Search**: Vector embeddings stored in Qdrant, query images by similarity.  
- 🔄 **Event-Driven Processing**: Kafka-powered pipeline for thumbnails, moderation, embeddings.  
- 🎨 **Frontend**: React-based gallery with secure login, upload & search.  
- 🛡️ **Security-first**: JWT-based API protection, controlled storage access.  

## 🏗️ Architecture

MiraVeja runs as a **set of services** in Docker Compose:

- **Core API (FastAPI)** → REST endpoints for frontend.  
- **Frontend (React/Vue)** → UI for browsing, uploads, search.  
- **Auth (Keycloak)** → Central identity provider with DeviantArt SSO.  
- **Database (Postgres)** → Asset metadata, users, marketplace.  
- **Object Storage (MinIO)** → Uploaded images & thumbnails.  
- **Vector DB (Qdrant)** → Embeddings for semantic search.  
- **Message Broker (Kafka)** → Async pipelines for processing.  
- **Worker Service (Python)** → Background jobs (embeddings, moderation, thumbnails).  

The [High-Level Container Diagram](./docs/diagrams/high-level-container.puml) illustrates the main components.

## 📦 Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: React (SPA)
- **Auth**: Keycloak
- **Database**: Postgres
- **Object Storage**: MinIO
- **Vector DB**: Qdrant
- **Messaging**: Kafka
- **Workers**: Python (embedding + processing jobs)
- **Infra**: Docker Compose

## 🚀 Getting Started

### 1. Clone Repository

```bash
git clone https://github.com/JomarJunior/miraveja.git
cd miraveja
```

### 2. Start Services

Use **Docker Compose** to bring up the environment:

```bash
docker-compose up -d
```

This will start:

- API (FastAPI)
- Frontend (React)
- Keycloak (Auth)
- Postgres (DB)
- MinIO (Object Storage)
- Qdrant (Vector Search)
- Kafka (Message Broker)
- Worker (Background Processing)

### 3. Access Services

- Frontend → [http://localhost:3000](http://localhost:3000)
- API → [http://localhost:8000/docs](http://localhost:8000/docs)
- Keycloak → [http://localhost:8080](http://localhost:8080)
- MinIO Console → [http://localhost:9001](http://localhost:9001)
- Qdrant → [http://localhost:6333](http://localhost:6333)

## 🔑 Authentication Setup

- Default authentication provider: **DeviantArt SSO**.
- Keycloak manages tokens and OIDC flows.
- To add more providers (Google, GitHub, etc.), configure them via Keycloak admin console.

## 🧪 Development Workflow

1. Code changes in `api/` (FastAPI) or `worker/` (Python).
2. Hot reload in FastAPI and React.
3. Use Kafka + Kafdrop for debugging event streams.
4. MinIO console for checking uploaded files.

## 🛤️ Roadmap

- **Phase 1 (MVP)** ✅

  - Auth via Keycloak + DeviantArt SSO.
  - Uploads to MinIO, metadata in Postgres.
  - Kafka ingestion pipeline.
  - Worker for embeddings + Qdrant indexing.
  - Search API + gallery frontend.

- **Phase 2**

  - Add more SSO providers.
  - Expand moderation features.
  - Add user reactions + basic recommendations.

- **Phase 3**

  - NFT minting service (IPFS + blockchain).
  - Marketplace with payments.
  - Deploy to Kubernetes.

## 📜 License

This project is licensed under the **MIT License** — free to use and modify.

## 🤝 Contributing

Contributions are welcome!
Open issues, submit PRs, or share ideas for improvements.

## 📊 Project Status

🚧 **Work in Progress (WIP)**: MVP in development.
Follow the roadmap for updates.
