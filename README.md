# 📋 Priority-Based Task Scheduler

A full-stack task scheduling application built with **Python** and **Streamlit**, powered by a **Min-Heap (Priority Queue)** data structure. Features user authentication, cloud database, REST API, animated heap visualizer, and productivity analytics.

## 🚀 Live Demo
👉 **[https://hardik-task-scheduler.streamlit.app](https://hardik-task-scheduler.streamlit.app)**

---

## 🧠 DSA Concepts Used

| Concept | Where Used |
|---|---|
| Min-Heap | Core scheduling engine (`scheduler.py`) |
| Priority Queue | Task ordering by urgency — O(log n) insert/delete |
| Stack (LIFO) | Undo system (`undo_stack.py`) |
| Command Pattern | Reversible actions via `Action` dataclass |
| Heapify | Auto-sort on every insert/delete |
| Dataclass | Clean task modeling (`task.py`) |

---

## ✨ Features

### Core
- ➕ Add tasks with name, priority (1–5), category, and optional deadline
- 📊 View all tasks sorted by priority in real-time (Min-Heap)
- ✅ Mark individual tasks as done
- ⚡ Quick-complete the highest priority task instantly
- ↩️ Undo last action (Stack-based — add or complete)
- 🕐 Auto-timestamp every task on creation
- 🎨 Color-coded priority indicators (🔴 Critical → ⚪ Low)
- 🏷️ Task categories (Work, Personal, Study, Health, Other)

### Visualizer
- 🌳 Animated D3.js heap tree — nodes animate in on every change
- 🖱️ Hover tooltips showing full task details
- 📊 Heap array view showing internal index order
- 🔴 Root node highlighted as MIN (highest priority)

### Analytics
- 📈 Tasks by category (donut chart)
- 📊 Tasks by priority (bar chart)
- 📅 Tasks completed per day (bar chart)
- 💯 Productivity score with smart insights

### Auth & Cloud
- 🔐 Secure signup and login
- 🔒 Passwords hashed with bcrypt
- 👤 Each user has private isolated task list
- ☁️ Powered by Supabase (PostgreSQL) — data never disappears

### API
- 🚀 Full REST API built with FastAPI
- 📖 Auto-generated Swagger UI at `/docs`
- GET, POST, DELETE endpoints for all operations

---

## 🗂️ Project Structure
```
task-scheduler/
├── app.py            # Streamlit UI + auth flow
├── scheduler.py      # Min-Heap Priority Queue
├── task.py           # Task dataclass
├── supabase_db.py    # Supabase cloud database layer
├── auth_manager.py   # Login/signup with bcrypt
├── visualizer.py     # D3.js animated heap tree
├── undo_stack.py     # Stack-based undo system
├── api.py            # FastAPI REST API
├── requirements.txt  # Dependencies
└── .streamlit/
    └── config.toml   # Dark theme config
```

---

## ⚙️ Setup & Run
```bash
# 1. Clone the repo
git clone https://github.com/Neardy11coder/task-scheduler.git
cd task-scheduler

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
# Create a .env file with:
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key

# 5. Run the Streamlit app
streamlit run app.py

# 6. Run the FastAPI server (optional)
uvicorn api:app --reload --port 8000
```

---

## 🔍 How the Heap Works
```
Add task    → heapq.heappush() → Min-Heap auto-sorts by priority
Complete    → heapq.heappop()  → Always removes Priority 1 first
Undo add    → remove from heap + mark complete in DB
Undo complete → restore to heap + mark pending in DB

Priority 1 (Critical) ← ROOT — always served first
Priority 2 (High)
Priority 3 (Medium)
Priority 4 (Low)
Priority 5 (Minimal) ← Always at bottom
```

---

## 🔍 How the Undo Stack Works
```
Add "Fix bug"      → push {ADD,  "Fix bug"}  to stack
Complete "Fix bug" → push {COMPLETE, "Fix bug"} to stack
Undo               → pop → reverse last action
Undo again         → pop → reverse one before that

Stack is LIFO — most recent action always undone first
Max size: 20 actions
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| GET | `/tasks` | Get all pending tasks |
| POST | `/tasks` | Add a new task |
| GET | `/tasks/next` | Peek at top priority task |
| DELETE | `/tasks/complete` | Complete top task |
| DELETE | `/tasks/undo` | Undo last action |
| GET | `/tasks/completed` | Get completed history |
| GET | `/stats` | Get pending/completed counts |
| DELETE | `/tasks/clear` | Clear all tasks |

Full interactive docs at `http://localhost:8000/docs`

---

## 🛠️ Built With

| Layer | Technology |
|---|---|
| UI | Streamlit |
| DSA Core | Python `heapq`, custom Stack |
| Visualizer | D3.js (via Streamlit components) |
| Charts | Plotly |
| Database | Supabase (PostgreSQL) |
| Auth | bcrypt + custom session management |
| REST API | FastAPI + Uvicorn |
| Deployment | Streamlit Cloud |

---

## 👨‍💻 Author

**Hardik** — B.Tech CS (First Year) | AI & DSA Enthusiast

> *"I built a task scheduler using a Min-Heap based Priority Queue in Python. The heap ensures O(log n) insertion and always serves the highest priority task first. I used a Stack for undo, Supabase for cloud persistence, FastAPI for REST API, and D3.js for live heap visualization."*

---

## 📄 License

MIT License — free to use and modify.