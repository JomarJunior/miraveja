# MiraVeja — Container Overview 🐳

MiraVeja is built as a **modular, containerized system** for managing AI-generated images.  
Each service runs in its own Docker container, making the system **portable, reproducible, and easy to develop**.  
This document explains **each container, its image, and its purpose**.

## 🐘 Postgres — `postgres:18.0-alpine`

**Purpose:** Primary database for storing structured data.  

- **What it does:**  
  Stores metadata about users, assets, tags, and marketplace listings.  
- **Why we use it:**  
  Postgres is **robust, open-source, ACID-compliant**, and supports complex queries and relational data.  
- **Ports:** 5432 (internal/external access for development).  
- **If not used:**  Metadata would need to be stored in a simpler key-value store (e.g., MinIO or JSON files), making queries like filtering assets by tags, user ownership, or search by creation date inefficient or very complex.  

## 🏗️ MinIO — `quay.io/minio/minio:RELEASE.2024-09-13T20-26-02Z`

**Purpose:** Object storage for uploaded images and thumbnails.  

- **What it does:**  
  Stores large binary objects (images) and provides an S3-compatible API for access.  
- **Why we use it:**  
  Lightweight, open-source, easy to integrate with Python clients, and fully compatible with cloud storage patterns.  
- **Ports:** 9000 (API), 9001 (Web console).  
- **If not used:**  Images could be stored on the filesystem inside the API container, but this would make scaling difficult, increase the risk of data loss, and complicate access from multiple services.  

## ⚡ Qdrant — `qdrant/qdrant:dev-3be4ca880519be040c45baafacd06f4dd4aee080`

**Purpose:** Vector database for semantic search.  

- **What it does:**  
  Stores embeddings generated from images and enables **approximate nearest neighbor search** for semantic similarity.  
- **Why we use it:**  
  Essential for AI-powered search and recommendations. Provides fast, scalable vector queries.  
- **Ports:** 6333 (API).  
- **If not used:** Semantic search would require scanning all images sequentially with Python scripts, which is extremely slow and not scalable. Text-only or metadata-only search would be possible but lose the AI-powered similarity functionality.  

## 🪵 Kafka — `bitnami/kafka:3.5`  

**Purpose:** Event streaming and messaging backbone.  

- **What it does:**  
  Handles events like `assets.uploaded`, `assets.processed`, and `user.reaction`.  
  Workers consume these events asynchronously to process images, generate embeddings, or update analytics.  
- **Why we use it:**  
  Enables **decoupled, event-driven architecture**, so services don’t block each other.  
- **Ports:** 9092 (Kafka broker).  
- **If not used:**  All processing would need to be synchronous in the API. Uploading an image would block until thumbnails, moderation, and embeddings are generated, slowing down user experience and making scaling more difficult.  

## 🌳 Zookeeper — `bitnami/zookeeper:3.8`

**Purpose:** Kafka coordination service.  

- **What it does:**  
  Keeps track of Kafka brokers, topics, and cluster state.  
- **Why we use it:**  
  Kafka (non-KRaft mode) requires Zookeeper for metadata management and broker coordination.  
- **Ports:** 2181 (client port).  
- **If not used:** Kafka cannot run in classic mode without Zookeeper. Without Zookeeper, either a single-node Kafka in KRaft mode or a different event system would be required.  

## 🛡️ Keycloak — `quay.io/keycloak/keycloak:25.0`

**Purpose:** Authentication and identity management.  

- **What it does:**  
  Handles user authentication via OAuth2/OpenID Connect. Supports DeviantArt SSO and can manage roles/permissions.  
- **Why we use it:**  
  Centralizes authentication, making it secure, extendable, and compatible with multiple identity providers.  
- **Ports:** 8080 (admin UI + user login).  
- **If not used:** The API would need to implement its own login system, password storage, token generation, and role management. This is **error-prone, less secure, and harder to extend** to social logins.  

## 🐍 API Service — `./api` (built from local Dockerfile)

**Purpose:** Core backend for MiraVeja.  

- **What it does:**  
  Provides REST API endpoints for uploading images, searching, and managing metadata.  
  Publishes Kafka events and interfaces with Postgres, MinIO, and Qdrant.  
- **Why we use it:**  
  Central service that coordinates all operations and exposes them to the frontend.  
- **If not used:** Frontend would need to communicate directly with Postgres, MinIO, Kafka, and Qdrant — tightly coupling the UI with backend logic and breaking separation of concerns.  

## 🛠️ Worker Service — `./worker` (built from local Dockerfile)

**Purpose:** Background processing for heavy or async tasks.  

- **What it does:**  
  Consumes Kafka events to generate thumbnails, run moderation checks, compute embeddings, and update Qdrant.  
- **Why we use it:**  
  Decouples heavy computation from the API to keep the frontend responsive and scalable.  
- **If not used:** All processing would need to happen synchronously in the API, slowing user requests and making it difficult to scale the system.  

## 🌐 Frontend — `./frontend` (built from local Dockerfile)

**Purpose:** User-facing interface.  

- **What it does:**  
  Provides a gallery interface for browsing, searching, and uploading images.  
  Handles authentication via Keycloak and communicates with the API.  
- **Why we use it:**  
  Delivers the **interactive user experience** while keeping the backend logic separated.  
- **Ports:** 3000 (development server).  
- **If not used:** Users would need to interact via Postman or command-line scripts. The system would lack a visual interface and user-friendly workflow.  

## ⚡ Traefik — `traefik:v3.0`

**Purpose:** Reverse proxy and entrypoint.  

- **What it does:**  
  Routes incoming HTTP requests to the appropriate backend service (API, frontend, Keycloak).  
  Provides a dashboard for monitoring routes.  
- **Why we use it:**  
  Simplifies networking in Docker Compose, supports HTTPS later, and centralizes routing.  
- **Ports:** 80 (HTTP), 8081 (Traefik dashboard).  
- **If not used:** Each service would need to expose its own port externally. Managing multiple services, SSL termination, or routing multiple domains would be more complex and error-prone.  

## 📝 Summary

Each container serves a **specific role** in MiraVeja:

- **Storage & database:** Postgres, MinIO  
- **AI & search:** Qdrant, Worker  
- **Messaging & orchestration:** Kafka, Zookeeper  
- **Authentication:** Keycloak  
- **Frontend / API / Reverse proxy:** Frontend, API, Traefik  

This design keeps the system **modular, maintainable, and easy to expand**, while letting developers **run the full stack locally** in Docker Compose.
