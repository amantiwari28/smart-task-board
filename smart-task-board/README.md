# 📋 Smart Task Board API

A full-featured task management REST API built with **FastAPI + MongoDB Atlas**, featuring JWT authentication, strict task status flow, and activity logging.

---

## 🚀 Live Demo
- **API Docs:** `https://your-app.onrender.com/docs`
- **Frontend:** `https://your-app.onrender.com/`

---

## ✨ Features

- 🔐 JWT authentication (register / login with token expiry)
- ✅ Create, view, and delete tasks
- 🔄 Strict status flow: `todo → in-progress → completed` (no skipping, no reversal)
- 📝 Activity log for every task event (create, update, delete)
- 📄 Paginated activity log endpoint
- 🧑‍💻 Simple HTML frontend to demo all features
- 📚 Auto-generated Swagger docs at `/docs`

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI |
| Database | MongoDB Atlas |
| ODM/Driver | Motor (async) |
| Auth | python-jose (JWT) + passlib (bcrypt) |
| Server | Uvicorn |
| Frontend | HTML + Vanilla JS |
| Deployment | Render |

---

## 📁 Project Structure

```
smart-task-board/
├── app/
│   ├── main.py          # App entry, middleware, routers
│   ├── database.py      # MongoDB connection
│   ├── schemas.py       # Pydantic models
│   ├── routers/
│   │   ├── auth.py      # Register & Login
│   │   ├── tasks.py     # CRUD + status flow
│   │   └── logs.py      # Paginated activity logs
│   └── utils/
│       ├── auth.py      # JWT helpers, password hashing
│       └── logger.py    # Activity log writer
├── templates/
│   └── index.html       # Frontend UI
├── main.py              # Dev entry point
├── requirements.txt
├── render.yaml          # Render deployment config
└── .env.example
```

---

## ⚙️ Environment Variables

Create a `.env` file in the project root (copy from `.env.example`):

| Variable | Description | Example |
|----------|-------------|---------|
| `MONGODB_URL` | MongoDB Atlas connection string | `mongodb+srv://user:pass@cluster.mongodb.net/` |
| `DB_NAME` | Database name | `smart_task_board` |
| `SECRET_KEY` | JWT signing secret (keep private!) | `my-secret-key-123` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry in minutes | `60` |

---

## 🖥 Local Setup

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/smart-task-board.git
cd smart-task-board
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your MongoDB Atlas URL and a secret key
```

### 5. Run the server
```bash
python main.py
# OR
uvicorn app.main:app --reload
```

### 6. Open in browser
- Frontend: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 📡 API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login, get JWT token |

### Tasks (🔒 Auth required)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/tasks/` | Create a task |
| GET | `/api/tasks/` | Get all your tasks |
| GET | `/api/tasks/{id}` | Get single task |
| PATCH | `/api/tasks/{id}/status` | Update status (strict flow) |
| DELETE | `/api/tasks/{id}` | Delete a task |

### Activity Logs (🔒 Auth required)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/logs/?page=1&per_page=10` | Paginated activity log |

---

## 🔄 Task Status Flow

```
todo  →  in-progress  →  completed
```

- Status **cannot skip** stages (todo → completed is rejected)
- Status **cannot go backward** (in-progress → todo is rejected)
- Completed tasks **cannot be changed**

---

## ☁️ Deploy to Render

1. Push code to GitHub
2. Go to [render.com](https://render.com) → **New Web Service**
3. Connect your GitHub repo
4. Set environment variables in Render dashboard:
   - `MONGODB_URL`
   - `SECRET_KEY`
   - `DB_NAME` = `smart_task_board`
   - `ACCESS_TOKEN_EXPIRE_MINUTES` = `60`
5. Build command: `pip install -r requirements.txt`
6. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
7. Click **Deploy**!

---

## 🗄 MongoDB Atlas Setup

1. Go to [mongodb.com/atlas](https://www.mongodb.com/atlas)
2. Create a free cluster (M0)
3. Add a database user with read/write permissions
4. Whitelist IP: `0.0.0.0/0` (for Render deployment)
5. Get connection string: **Connect → Drivers → Copy URI**
6. Paste into your `.env` as `MONGODB_URL`
