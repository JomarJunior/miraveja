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
