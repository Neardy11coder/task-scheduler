# 📋 Priority-Based Task Scheduler

A full-stack task scheduling application built with **Python** and **Streamlit**, powered by a **Min-Heap (Priority Queue)** data structure.

## 🚀 Live Demo
> Run locally — instructions below

## 🧠 DSA Concepts Used
| Concept | Where Used |
|---|---|
| Min-Heap | Core scheduling engine (`scheduler.py`) |
| Priority Queue | Task ordering by urgency |
| Dataclass | Clean task modeling (`task.py`) |
| Heapify | Auto-sort on every insert/delete |

## ✨ Features
- ➕ Add tasks with name, priority (1–5), and optional deadline
- 📊 View all tasks sorted by priority in real-time
- ✅ Mark individual tasks as done
- ⚡ Quick-complete the highest priority task instantly
- 🕐 Auto-timestamp every task on creation
- 🎨 Color-coded priority indicators (🔴 Critical → ⚪ Low)

## 🗂️ Project Structure
```
task-scheduler/
├── app.py          # Streamlit UI
├── scheduler.py    # Min-Heap Priority Queue
├── task.py         # Task dataclass
└── requirements.txt
```

## ⚙️ Setup & Run
```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/task-scheduler.git
cd task-scheduler

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

## 🔍 How the Heap Works
```
Add tasks → heapq.heappush() → Min-Heap auto-sorts
Complete task → heapq.heappop() → Always removes lowest priority number first

Priority 1 (Critical) ← Always at top of heap
Priority 2 (High)
Priority 3 (Medium)
Priority 4 (Low)
Priority 5 (Minimal) ← Always at bottom
```

## 🛠️ Built With
- Python 3.x
- Streamlit
- heapq (Python standard library)

## 👨‍💻 Author
**Hardik** — B.Tech CS | AI & DSA Enthusiast