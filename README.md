# tsumiki v0.1.0

> A solo full-stack practice project

## Project Structure

├── tsumiki-backend/ # FastAPI – the brain behind the curtain

└── tsumiki-frontend/ # Vue 3 – the face you see

---

## Backend Stack

| Layer                         | Technology                                                                  |
| ----------------------------- | --------------------------------------------------------------------------- |
| ASGI Application              | FastAPI                                                                     |
| ASGI Server                   | Uvicorn                                                                     |
| Schema & Serialization        | Pydantic + Pydantic‑settings                                                |
| ORM                           | SQLAlchemy                                                                  |
| Database                      | PostgreSQL                                                                  |
| Database Migration            | Alembic                                                                     |
| Auth                          | JWT + bcrypt                                                                |
| Storage                       | Local disk with metadata‑driven file management                             |

---

## Frontend Stack

| Layer                         | Technology                                                                  |
| ----------------------------- | --------------------------------------------------------------------------- |
| Framework                     | Vue 3                                                                       |
| Build Tool                    | Vite                                                                        |
| State Management              | Pinia                                                                       |
| Routing                       | Vue Router                                                                  |
| Language                      | TypeScript                                                                  |
| UI Components                 | Naive UI                                                                    |
| Live2D                        | live2d‑widget.js by [@xiazeyu](https://github.com/xiazeyu)                  |
| Live2D Model                  | tsumiki                                                                     |

---

## Quick Start

```bash
# Clone the repo
git clone https://github.com/Sappfly/tsumiki.git
cd tsumiki

# Backend
cd tsumiki-backend
cp .env.example .env          # edit with your own secrets
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python3 run.py --dev

# Frontend
cd ../tsumiki-frontend
cp .env.example .env          # edit with your own config
npm install
npm run dev
```

---

## Thanks

Thanks [xiazeyu / live2d-widget.js](https://github.com/xiazeyu/live2d-widget.js) – for the adorable front‑end mascot

> Thanks to [UNPKG](https://unpkg.com/) for providing public CDN service.



