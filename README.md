MiraVeja - Pre-Alpha
===

![MiraVeja Logo](images/logo.png)

MiraVeja is a small-scale, production-style personal project that blends web development and machine learning. It automatically fetches images from a provider, stores them with metadata, and uses modern deep learning models to generate embeddings for text-to-image and image-to-image semantic search.

The project is designed to be simple to run yet architecturally clean, showcasing professional patterns like dependency injection, event-driven actions, and modular service containers — all while remaining approachable as a portfolio project.

💡 The Idea
---

We live in a time where **AI and machine learning** have completely changed the way we interact with images. One of the most fascinating concepts to come out of this is something called the **Latent Space**.  

In simple terms, the latent space is a kind of “hidden map” where images (and sometimes text) are represented as long lists of numbers — vectors — in a high-dimensional space. These numbers aren’t random; they capture both the **visual details** (colors, shapes, textures) and the **semantic meaning** (what the image actually *is* about).  

The amazing part is that we can also encode **text** into the *same* latent space. That means an image of “a red car” and the text “red sports car” end up close together on this map. Because of this, we can search not just by filenames or tags, but by meaning — finding images that “feel” like the description we give, or finding similar images to one we already have.  

That’s the power I want to bring into MiraVeja:

- Download images automatically from a provider  
- Store them neatly with their metadata  
- Generate embeddings (their “coordinates” in latent space)  
- Let me search and explore my gallery based on meaning, not just keywords  

It’s not about building a massive search engine — it’s about having a **smart, personal gallery** that understands the images the way I do.  

📦 Tech Stack
---

Below you'll find an overview of the core technologies and tools used in MiraVeja. Each layer of the stack is listed with its purpose, helping you understand how the project is structured and why each component was chosen.

| Layer | Tool | Reason |
|-------|------|--------|
| **Backend** | 🐍 *Python 3.13 +* 🧪 *Flask 3.1* | Lightweight REST API framework |
| **ORM** | 🧙‍♂️ *SQLAlchemy 2.x* | Powerful and flexible ORM for database interactions |
| **DB Versioning** | ⚗️ *Alembic* | Official tool for SQLAlchemy migrations |
| **Database** | 🗄️ *PostgreSQL 15* | Reliable and feature-rich relational database, handles metadata + embeddings in one place |
| **Image Storage** | 💾 *Filesystem* | Avoids storing large binary blobs in DB |
| **Image Processing** | 🛏️ *Pillow* | Basic image transformation |
| **Embeddings** | 🔦 *Torch +* 📎 *CLIP* | Decoupled ML pipeline |
| **Frontend** | 👁️ *Vue.js 3 +* ✨ *Vuetify* | Responsive and polished UI |
| **Containerization** | 🐳 *Docker* | Portable deployment |
| **DI** | 🧩 *In-house Dependency Injector* | Customizable and flexible dependency injection system |
| **Event System** | 🔄 *In-house Event System* | Custom event handling and messaging system |
| **Testing** | 🐛 *Pytest* | Comprehensive testing framework for Python |
| **CI/CD** | 🛠️ *GitHub Actions* | Automated testing and deployment pipeline |

📁 Directory Structure
---

The project follows a Domain-Driven Design (DDD) with Hexagonal Architecture principles, organizing code by bounded contexts:

```text
miraveja/
├── README.md                           # Project overview and documentation
├── requirements.txt                    # Python dependencies
├── docker-compose.yml                 # Container orchestration
├── .env.example                       # Environment variables template
│
├── .github/                           # GitHub Actions workflows
│   └── workflows/
│       ├── ci.yml                    # CI workflow
│       └── cd.yml                    # CD workflow
│
├── docs/                              # Architecture diagrams and documentation
│   ├── context-diagram.puml          # DDD bounded contexts
│   ├── components-diagram.puml       # Component architecture
│   ├── blocks-diagram.puml          # System architecture
│   ├── data-flow-diagram.puml       # Data flow visualization
│   └── requirements.md               # Detailed requirements
│
├── tools/
│   ├── __init__.py
│   └── generate_init_files.py        # Utility to generate __init__.py files
│
├── api/                              # Backend API
│   ├── main.py                       # Application entry point
│   └── src/                          # Source code
│       ├── config/                   # Configuration management
│       │   ├── __init__.py
│       │   ├── settings.py          # App settings and environment variables
│       │   └── database.py          # Database configuration
│       │
│       ├── core/                     # Cross-cutting concerns and shared kernel
│       │   ├── __init__.py
│       │   ├── di/                   # Dependency Injection container
│       │   │   ├── __init__.py
│       │   │   ├── container.py     # DI container implementation
│       │   │   └── interfaces.py    # DI abstractions
│       │   ├── events/               # Event system
│       │   │   ├── __init__.py
│       │   │   ├── bus.py          # Event bus implementation
│       │   │   └── base.py         # Base event classes
│       │   └── exceptions/           # Custom exceptions
│       │       ├── __init__.py
│       │       └── base.py          # Base exception classes
│       │
│       ├── acquisition/             # Image acquisition context
│       │   ├── __init__.py
│       │   ├── domain/              # Domain models and business logic
│       │   │   ├── __init__.py
│       │   │   ├── exceptions.py    # Domain-specific exceptions
│       │   │   ├── events.py        # Domain events
│       │   │   ├── entities.py      # Domain entities
│       │   │   ├── value_objects.py  # Domain value objects
│       │   │   ├── services.py      # Domain services
│       │   │   └── interfaces.py    # Domain interfaces
│       │   ├── infrastructure/      # External adapters
│       │   │   ├── __init__.py
│       │   │   ├── providers.py     # Image provider adapters
│       │   │   ├── subscribers.py   # Event subscribers
│       │   │   ├── dependencies.py  # Dependency injection
│       │   │   ├── repositories.py  # Repository implementations
│       │   │   └── http/            # API controllers and routes for this context
│       │   │       ├── __init__.py
│       │   │       ├── routes.py       # HTTP routes
│       │   │       └── controller.py   # HTTP request handlers
│       │   └── application/         # Application services
│       │       ├── __init__.py
│       │       ├── handlers.py      # Use case handlers
│       │       └── commands.py      # Use case commands
│       │
│       ├── processing/              # ML/AI processing context
│       │   ├── __init__.py
│       │   ├── domain/              # Domain models and business logic
│       │   │   ├── __init__.py
│       │   │   ├── exceptions.py    # Domain-specific exceptions
│       │   │   ├── events.py        # Domain events
│       │   │   ├── entities.py      # Domain entities
│       │   │   ├── value_objects.py  # Domain value objects
│       │   │   ├── services.py      # Domain services
│       │   │   └── interfaces.py    # Domain interfaces
│       │   ├── infrastructure/      # External adapters
│       │   │   ├── __init__.py
│       │   │   ├── embedding_services.py  # Embedding services implementation
│       │   │   ├── subscribers.py   # Event subscribers
│       │   │   ├── dependencies.py  # Dependency injection
│       │   │   ├── repositories.py  # Repository implementations
│       │   │   └── http/            # API controllers and routes for this context
│       │   │       ├── __init__.py
│       │   │       ├── routes.py
│       │   │       └── controller.py
│       │   └── application/
│       │       ├── __init__.py
│       │       ├── handlers.py      # Use case handlers
│       │       └── commands.py      # Use case commands
│       │
│       ├── retrieval/               # Search and retrieval context
│       │   ├── __init__.py
│       │   ├── domain/              # Domain models and business logic
│       │   │   ├── __init__.py
│       │   │   ├── exceptions.py    # Domain-specific exceptions
│       │   │   ├── events.py        # Domain events
│       │   │   ├── entities.py      # Domain entities
│       │   │   ├── value_objects.py  # Domain value objects
│       │   │   ├── services.py      # Domain services
│       │   │   └── interfaces.py    # Domain interfaces
│       │   ├── infrastructure/      # External adapters
│       │   │   ├── __init__.py
│       │   │   ├── search_engine.py # Vector search implementation
│       │   │   ├── subscribers.py   # Event subscribers
│       │   │   ├── dependencies.py  # Dependency injection
│       │   │   ├── repositories.py  # Repository implementations
│       │   │   └── http/            # API controllers and routes for this context
│       │   │       ├── __init__.py
│       │   │       ├── routes.py
│       │   │       └── controller.py
│       │   └── application/
│       │       ├── __init__.py
│       │       ├── handlers.py      # Use case handlers
│       │       └── commands.py      # Use case commands
│       │
│       └── storage/                 # Persistence context
│           ├── __init__.py
│           ├── domain/              # Domain models and business logic
│           │   ├── __init__.py
│           │   ├── exceptions.py    # Domain-specific exceptions
│           │   ├── events.py        # Domain events
│           │   ├── entities.py      # Domain entities
│           │   ├── value_objects.py  # Domain value objects
│           │   ├── services.py      # Domain services
│           │   └── interfaces.py    # Domain interfaces
│           ├── infrastructure/
│           │   ├── __init__.py
│           │   ├── database.py      # PostgreSQL implementation
│           │   ├── filesystem.py    # File system storage
│           │   ├── encryption.py    # Encryption services
│           │   ├── subscribers.py   # Domain event subscribers
│           │   ├── dependencies.py  # Dependency injection
│           │   ├── http/            # API controllers and routes for this context
│           │   │   ├── __init__.py
│           │   │   ├── routes.py
│           │   │   └── controller.py
│           │   └── migrations/      # Database migrations (Alembic)
│           │       ├── __init__.py
│           │       └── versions/    # Migration versions
│           └── application/
│               ├── __init__.py
│               ├── handlers.py      # Use case handlers
│               └── commands.py      # Use case commands
│
├── client/                          # Frontend application
│   ├── package.json                 # Frontend dependencies
│   ├── vite.config.js               # Vite configuration
│   ├── index.html                   # Main HTML file
│   ├── src/
│   │   ├── main.js                  # Vue app entry point
│   │   ├── App.vue                  # Root component
│   │   ├── components/              # Vue components
│   │   │   └── ...
│   │   ├── store/                   # Pinia store
│   │   │   ├── app.js               # App-specific state
│   │   │   ├── notification.js      # Notification state
│   │   │   └── ...
│   │   ├── views/                   # Page components
│   │   │   ├── Home.vue             # Home page
│   │   │   └── ...
│   │   ├── api/                      # API service clients
│   │   │   ├── http-client.js       # Luxon HTTP client configuration
│   │   │   ├── acquisition.js       # Acquisition API client
│   │   │   ├── processing.js        # Processing API client
│   │   │   └── retrieval.js         # Retrieval API client
│   │   └── assets/                  # Static assets
│   └── public/                      # Public static files
│
├── tests/                           # Test suite
│   ├── __init__.py
│   ├── unit/                        # Unit tests
│   │   ├── acquisition/             # Context-specific tests
│   │   ├── processing/
│   │   ├── retrieval/
│   │   ├── storage/
│   │   └── core/                    # Core functionality tests
│   ├── integration/                 # Integration tests
│   └── e2e/                        # End-to-end tests
│
├── storage/                         # Local file storage
│   ├── images/                      # Downloaded images
│   ├── thumbnails/                  # Generated thumbnails
│   └── temp/                        # Temporary files
│
└── deployment/                      # Deployment configurations
    ├── Dockerfile.api               # API container definition
    ├── Dockerfile.client            # Client container definition
    ├── docker-compose.prod.yml     # Production compose
    └── k8s/                        # Kubernetes manifests (if needed)
        ├── api-deployment.yaml
        ├── client-deployment.yaml
        └── service.yaml
```

This structure supports:

- **Domain-Driven Design**: Each bounded context has its own domain, infrastructure, and application layers
- **Hexagonal Architecture**: Clear separation between core business logic and external adapters
- **Context-Owned Controllers**: Each context manages its own API controllers and routes
- **Frontend/Backend Separation**: Clear separation between client and API applications
- **Dependency Injection**: Centralized DI container for managing dependencies
- **Event-Driven Architecture**: Decoupled communication via event bus
- **Clean Testing**: Organized test structure matching the application architecture
