# 📋 Priority-Based Task Scheduler

A full-stack task management application built with **Python, Streamlit, and FastAPI**, powered by a **Min-Heap (Priority Queue)** data structure.

The application helps users organize tasks according to urgency, manage deadlines, track productivity, and understand how priority-based scheduling works through an interactive heap visualization.

🚀 **[Live Demo](https://hardik-task-scheduler.streamlit.app)**

---

## ✨ Features

### 📌 Task Management
- Add tasks with a name, priority (1–5), category, and optional deadline.
- View pending tasks organized by priority.
- Mark individual tasks as completed.
- Instantly complete the highest-priority task.
- Undo supported actions using a Stack-based undo system.
- Automatically timestamp tasks when created.
- Color-coded priority indicators.
- Organize tasks into Work, Personal, Study, Health, and Other categories.

### 🌳 Interactive Heap Visualizer
- Animated D3.js heap tree visualization.
- Nodes animate when the heap changes.
- Interactive hover tooltips displaying task information.
- Heap array visualization showing internal index positions.
- Root node highlighted to represent the next highest-priority task.

### 📊 Productivity Analytics
- Tasks grouped by category (donut chart).
- Tasks grouped by priority (bar chart).
- Daily task completion statistics.
- Productivity score and insights.

### 🔐 Authentication & Cloud Database
- User signup and login.
- Password hashing using bcrypt.
- User-specific task storage.
- Supabase-powered PostgreSQL database.
- Persistent task storage across sessions.

### ⚡ REST API
- FastAPI-based REST API.
- Endpoints for task creation, retrieval, completion, and undo operations.
- Automatic interactive API documentation through Swagger UI.

---

## 🧠 Data Structures & Algorithms

The project demonstrates the practical application of fundamental data structures.

| Concept | Implementation | Complexity |
|---|---|---|
| Min-Heap | Core task scheduling engine | O(log n) insertion/deletion |
| Priority Queue | Task ordering by urgency | O(1) peek |
| Stack (LIFO) | Undo functionality | O(1) push/pop |
| Heap Operations | `heapq.heappush()` and `heapq.heappop()` | O(log n) |
| Dataclasses | Structured task representation | — |
| Command Pattern | Reversible actions using Action dataclass | — |

### Priority System

| Priority | Level | Meaning |
|---|---|---|
| 1 | 🔴 Critical | Highest urgency |
| 2 | 🟠 High | High urgency |
| 3 | 🟡 Medium | Normal urgency |
| 4 | 🔵 Low | Low urgency |
| 5 | ⚪ Minimal | Lowest urgency |

The application uses a Min-Heap, where the smallest priority value is treated as the highest urgency.

**Important:** A heap guarantees that the minimum-priority element is at its root. It does not maintain a completely sorted array internally.

---

## 🔄 How the Heap Works

The scheduling engine uses Python's built-in `heapq` module.

```python
# Insert a task
heapq.heappush(heap, task)

# Retrieve the highest-priority task
next_task = heap[0]

# Remove the highest-priority task
completed_task = heapq.heappop(heap)
```

The heap maintains its ordering property after insertion and removal.

### Undo Stack

The undo mechanism follows the Last In, First Out (LIFO) principle.

```text
Add task       → Push ADD action onto stack
Complete task  → Push COMPLETE action onto stack

Undo           → Pop most recent action
Undo again     → Reverse the previous action
```

The undo system supports up to 20 actions.

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Programming Language | Python |
| DSA Core | Python `heapq`, Custom Stack |
| Visualization | D3.js |
| Charts | Plotly |
| Backend API | FastAPI |
| ASGI Server | Uvicorn |
| Database | Supabase (PostgreSQL) |
| Authentication | bcrypt, Custom Session Management |
| Deployment | Streamlit Community Cloud |

---

## 🗂️ Project Structure

```text
task-scheduler/
│
├── app.py                 # Streamlit UI and authentication
├── scheduler.py           # Min-Heap priority scheduling
├── task.py                # Task dataclass
├── supabase_db.py         # Supabase database operations
├── auth_manager.py        # Authentication and password hashing
├── visualizer.py          # Interactive D3.js visualization
├── undo_stack.py          # Stack-based undo system
├── api.py                 # FastAPI REST API
│
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variable template
├── .gitignore             # Files excluded from Git
├── LICENSE                # MIT License
│
└── .streamlit/
    └── config.toml        # Streamlit theme configuration
```

---

## ⚙️ Installation & Setup

### Prerequisites

- Python installed on your system.
- Git.
- A Supabase project with the required database schema and credentials.

### 1. Clone the repository

```bash
git clone https://github.com/Neardy11coder/task-scheduler.git

cd task-scheduler
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

**Windows PowerShell**
```powershell
.venv\Scripts\Activate.ps1
```

**Windows CMD**
```cmd
.venv\Scripts\activate.bat
```

**macOS / Linux**
```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root.

```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
```

Replace the placeholders with your actual Supabase credentials.

**Security note:** Never commit your `.env` file, database passwords, or private API keys to GitHub.

### 5. Run the Streamlit application

```bash
streamlit run app.py
```

The application will be available at:

```text
http://localhost:8501
```

### 6. Run the FastAPI server

Open another terminal, activate the virtual environment, and execute:

```bash
uvicorn api:app --reload --port 8000
```

Interactive API documentation:

```text
http://localhost:8000/docs
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | API health check |
| GET | `/tasks` | Retrieve pending tasks |
| POST | `/tasks` | Add a new task |
| GET | `/tasks/next` | View the highest-priority task |
| DELETE | `/tasks/complete` | Complete the highest-priority task |
| DELETE | `/tasks/undo` | Undo the last supported action |
| GET | `/tasks/completed` | Retrieve completed task history |
| GET | `/stats` | Retrieve productivity statistics |
| DELETE | `/tasks/clear` | Clear all tasks |

---

## 🎯 Learning Objectives

This project was developed to explore the practical implementation of:

- Priority Queues and Min-Heap data structures.
- Stack-based state reversal.
- Time complexity and efficient task scheduling.
- Full-stack application development.
- REST API design using FastAPI.
- Authentication and database integration.
- Interactive data visualization using D3.js.
- Cloud deployment and persistent storage.

---

## 🤝 Contributing

Contributions, suggestions, and improvements are welcome.

To contribute:

1. Fork this repository.
2. Create a new feature branch.
3. Implement your changes.
4. Test your changes locally.
5. Submit a pull request with a clear description.

Please keep contributions focused, documented, and consistent with the project's architecture.

---

## 👨‍💻 Author

**Hardik Kapil**

B.Tech Computer Science and Engineering (AI & ML) | Third Year

Interested in Software Development, Data Structures & Algorithms, and Artificial Intelligence.

> "Building practical software is one of the best ways to understand the data structures and algorithms behind it."

---

## 📄 License

This project is licensed under the **MIT License**.

See the [`LICENSE`](LICENSE) file for the complete license text.

---

⭐ If you find this project useful, consider giving it a star on GitHub!

**Repository:** https://github.com/Neardy11coder/task-scheduler
