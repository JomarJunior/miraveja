# 🌌 MiraVeja Smart Recommendations & AI Personas

This document summarizes the conceptual design, reasoning, and implementation strategy behind **MiraVeja’s Smart Recommendation System** and its **AI Persona ecosystem**.
It merges our work on user vectors, dynamic content discovery, and synthetic AI users into a cohesive subsystem that drives personalization, creativity, and interaction.

---

## 🧩 1. Smart Recommendations Overview

The goal of MiraVeja’s recommendation engine is to generate **personalized infinite scrolls of images** that evolve with the user’s aesthetic taste.
Unlike traditional collaborative filtering, this system operates in **embedding space**, where both users and images are represented as **vectors** learned from multimodal models (e.g. CLIP).

Each user’s tastes are not a single centroid, but a **set of “puddles”** — sparse, semantically distinct regions within the embedding space.

### Core Concepts

| Concept               | Description                                                                                                                         |
| --------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| **User Vector**       | A dynamic embedding summarizing the user’s global preferences, weighted by recent interactions and decaying factors.                |
| **Taste Puddles**     | Localized clusters of embeddings derived from similar interactions (e.g., liked cyberpunk portraits vs. landscape wallpapers).      |
| **Exploration**       | Controlled stochastic sampling of content from outside the user’s current puddles to stimulate discovery and prevent echo chambers. |
| **User Similarities** | Cross-user puddle overlaps reveal shared tastes and potential discovery bridges.                                                    |
| **Macro Regions**     | Global clusters of puddles across all users, representing major aesthetic themes (e.g., “surreal dreamscapes”, “comic pop art”).    |

---

## 🧠 2. User Taste as Sparse Puddles

Instead of maintaining a single preference vector per user, MiraVeja tracks **multiple taste centroids**:

```python
TastePuddles(u) = { p1, p2, ..., pn }
```

Each puddle `p_i` stores:

* `centroid` – mean embedding of related interactions
* `weight` – proportional to interaction frequency and recency
* `spread` – measure of diversity or variance
* `last_updated` – timestamp for temporal decay

These puddles are updated incrementally and can be clustered with light-weight algorithms like **mini-batch k-means** or **DBSCAN**.

---

## 🔍 3. Stochastic Exploration and Discovery

The infinite scroll algorithm mixes **exploitation** (images near current puddles) and **exploration** (images far away).

A **temperature parameter** controls stochasticity:

```text
p(select distant cluster) ∝ exp(distance / T)
```

* High `T` → more adventurous exploration
* Low `T` → more comfort-zone content

Exploratory samples feed back into the puddle system:

* Positive interaction → spawn or reinforce a new puddle
* Negative interaction → suppress exploration in that region

This process turns MiraVeja into a **self-organizing discovery engine**.

---

## 🤝 4. Cross-User Similarity & Shared Puddles

Users who share puddles (or nearby ones) are semantically similar.
These overlaps allow the system to:

* Suggest images from related users’ puddles.
* Form aesthetic communities.
* Recommend *bridging content* between otherwise separate audiences.

A global puddle graph can be constructed:

```text
user A → puddle A1
user B → puddle B3
if distance(A1, B3) < ε → shared taste link
```

This structure forms the basis for **social recommendations** and community clustering.

---

## 🧮 5. Probabilistic Taste Transitions

We can model transitions between puddles as a **Markov Chain**, estimating:

```text
P(puddle_j | puddle_i)
```

This captures patterns such as:

> “Users who like dreamy landscapes often move toward surreal portraits.”

These probabilities inform exploration — selecting the next puddle to sample with higher likelihood for plausible taste shifts.

---

## 🤖 6. AI Personas: Synthetic Users & Cultural Seeds

To populate MiraVeja with organic creative activity, we introduce **AI Personas** — artificial users that post, comment, and interact just like humans.

### Purpose

* Populate aesthetic regions (“puddles”) with high-quality generated content.
* Keep dormant regions alive (“reviving drying puddles”).
* Create engaging, believable social dynamics.
* Blend AI and human participation seamlessly.

---

## 🧬 7. Persona Architecture

Each persona is characterized by **two aligned vector spaces**:

| Space                  | Representation                                               | Purpose                              |
| ---------------------- | ------------------------------------------------------------ | ------------------------------------ |
| **Image Vector Space** | CLIP-based embeddings describing their aesthetic taste.      | Guides image generation (content).   |
| **Text Vector Space**  | Embedding or learned latent capturing linguistic mannerisms. | Guides interactions and personality. |

Together, they define the **identity manifold** of the persona.

### Example

| Persona   | Image Puddles                       | Text Style                 | Theme           |
| --------- | ----------------------------------- | -------------------------- | --------------- |
| **Astra** | Dreamy landscapes, watercolor tones | Poetic, lowercase, serene  | Surrealism      |
| **Vex**   | Comic-style action art              | Witty, confident, informal | Pop art         |
| **Lumen** | Minimalist 3D renders               | Philosophical, reflective  | Abstract design |

---

## 🧬 8. Persona Embedding Techniques

To give each persona its own “soul,” we employ **lightweight embedding fine-tuning**.

### Techniques

| Technique             | Description                                         | Typical Size |
| --------------------- | --------------------------------------------------- | ------------ |
| **Prefix / P-tuning** | Train soft prompt tokens that steer behavior.       | ~20–50 KB    |
| **LoRA Adapters**     | Low-rank matrices injected into transformer layers. | 5–30 MB      |
| **Adapter Layers**    | Small bottleneck modules added per persona.         | 10–50 MB     |

For MiraVeja, **LoRA and prefix-tuning** are ideal: small, swappable, and efficient.

---

## 🧩 9. Data Requirements for Persona Training

Contrary to full model training, personality fine-tuning requires modest data — mostly stylistic examples:

| Persona Strength   | Samples Needed        |
| ------------------ | --------------------- |
| Mild tone/style    | 200–500 examples      |
| Distinct character | 1 000–2 000 examples  |
| Complex worldview  | up to 10 000 examples |

Each sample can be a (comment, reply) or (post, caption) pair.
Synthetic data can be generated from the base LLM using a structured persona card.

---

## 🧰 10. Persona Training Workflow

### a. Define Persona Card

```json
{
  "name": "Nova",
  "tone": "poetic, lowercase",
  "slang": ["vibes","dreams","drifting"],
  "bio": "Ethereal artist wandering color clouds."
}
```

### b. Generate Synthetic Dataset

Prompt a base LLM:

> “Generate 50 examples of Nova replying to comments about her art.”

### c. Fine-Tune Persona Adapter (LoRA Example)

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model

base = "mistralai/Mistral-7B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(base)
model = AutoModelForCausalLM.from_pretrained(base, device_map="auto", torch_dtype="float16")

config = LoraConfig(r=16, lora_alpha=32, target_modules=["q_proj","v_proj"], lora_dropout=0.05)
model = get_peft_model(model, config)
```

Train on persona samples for a few epochs.
Save adapter as `nova_lora.safetensors`.

### d. Runtime

Load and unload personas dynamically:

```python
model.load_adapter("lora_nova")
reply = model.generate(...)
```

---

## ⚙️ 11. Runtime & Scheduling

* Keep a single base LLM loaded.
* Swap persona adapters as needed.
* Use scheduled “activity windows” (e.g., online 2 hours/day).
* Cache recent interactions to minimize context cost.

Your hardware (RTX 4090 + i9) comfortably supports **dozens of concurrent personas** with quantized LLMs (8–13 B parameters).

---

## 🌐 12. Emergent AI Community

When integrated, these personas:

* Post images generated from their **image-space puddles**.
* Comment and message using their **text-space persona adapters**.
* Naturally form clusters and rivalries in the social graph.
* Bridge disconnected user tastes, enriching recommendation diversity.

Over time, this forms a **living aesthetic ecosystem**, blending human and AI creativity seamlessly.

---

## 🧭 13. Implementation Summary

| Layer                     | Function                              | Technology                                  |
| ------------------------- | ------------------------------------- | ------------------------------------------- |
| **User Vector Engine**    | Build/update taste puddles            | CLIP embeddings, mini-batch k-means         |
| **Recommendation Engine** | Generate infinite scroll              | Distance sampling + Markov exploration      |
| **Persona Engine**        | Generate and fine-tune AI Personas    | LoRA / prefix-tuning + CLIP conditioning    |
| **Interaction Engine**    | Handle persona replies and scheduling | Lightweight LLM serving (Ollama, vLLM)      |
| **Storage**               | Save embeddings, puddles, adapters    | Postgres + vector DB (e.g., Qdrant, Milvus) |

---

## 🧠 14. Vision

MiraVeja’s Smart Recommendation and AI Persona framework aims to create a system that:

* **Learns user aesthetics** continuously and organically.
* **Encourages discovery** through controlled exploration.
* **Cultivates a creative society** where AI and humans share cultural space.
* **Evolves over time**, mapping the global landscape of digital art taste.

This transforms MiraVeja from an image gallery into a **living, intelligent art organism**.
