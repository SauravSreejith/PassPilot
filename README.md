# CODERECET: PassPilot

## 🔗 Project Repository

### 👥 Team Name: Stardust Crusaders  
**Members**: Anagha K, Saurav Sreejith, Shreya Padmakumar, S Murugan

---

## 📘 Project Description

**PassPilot** is an AI-assisted exam survival guide tailored for KTU students. It optimizes exam prep under tight deadlines using historical PYQ data and topic frequency analysis to generate personalized, minimum-effort study plans aimed at reaching the 40/100 pass threshold.

PassPilot implements scoring algorithms that consider topic frequency, difficulty, and expected yield. The platform supports:

- **Survival Track**: Minimum viable prep.
- **Excellence Track**: Extended, deeper study path.
- **Crisis Mode**: Last-minute planner with an effort-to-marks estimator.

Built on a modular architecture, PassPilot features a real-time pass probability estimator and topic recommendations.

---

## 🛠️ Technologies & Components

### 📦 Backend (Engine)

- **Language**: Python 3.10+
- **Frameworks**:
  - `Flask` – REST API
  - `LangChain` – RAG orchestration
- **Libraries**:
  - `sentence-transformers` – Semantic vector embeddings
  - `scikit-learn` – Cosine similarity
  - `numpy` – Numerical simulations
  - `langchain-google-genai` – Gemini LLM + Embeddings
  - `chromadb` – Persistent vector store
  - `pypdf` – PDF parsing
  - `python-dotenv` – Secure env var handling
  - `flask-cors` – CORS for frontend

### 🌐 Frontend

- **Repo**: [SauravSreejith/passpilot-web](https://github.com/SauravSreejith/passpilot-web)
- **Framework**: React.js (Vite)
- **Language**: TypeScript
- **Styling**:
  - `tailwindcss`
  - `shadcn/ui`
- **Libraries**:
  - `react-router-dom` – Routing
  - `lucide-react` – Icons
- **Tools**:
  - `Vite` – Build tool
  - `npm` – Package manager

---

## ⚙️ Installation

### Prerequisites

- Python 3.10+ and `pip`
- Node.js and `npm`
- Google Gemini API Key

The project has **two repos**: backend and frontend. Clone and set up both.

---

### 🔧 Backend Setup

```bash
# Clone the backend repo
git clone <your-backend-repository-url>
cd engine  # or your backend folder

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
touch .env
# Then edit it with your Gemini key
# e.g., nano .env
````

Your `.env` should contain:

```env
GEMINI_API_KEY="AIzaSy...YOUR_API_KEY_HERE"
```

---

### 🎨 Frontend Setup

```bash
# In a separate folder
git clone https://github.com/SauravSreejith/passpilot-web.git
cd passpilot-web

# Install frontend dependencies
npm install
```

---

## 🚀 Running the App

You’ll need **two terminals**: one for backend, one for frontend.

---

### ▶️ Start Backend

```bash
# In backend directory
source venv/bin/activate
python run_server.py
```

> The backend runs on `http://localhost:5000`.

---

### ▶️ Start Frontend

```bash
# In frontend directory
npm run dev
```

> The frontend runs on `http://localhost:5173`.

---

## 📚 Project Documentation

### 🎯 Vision: From Anxiety to Strategy

PassPilot tackles *study paralysis* — the fear of too much to study in too little time. It reframes exam prep as a **strategic allocation problem**. No more "study everything"; instead: *"study smart, survive efficiently."*

---

### 🧠 Component 1: Exam Analysis Engine (`ExamAnalyzer`)

#### 📌 Semantic Question Analysis

* **Model**: `all-MiniLM-L6-v2`
* **Goal**: Understand question *meaning*, not just keywords
* **Method**: Embed both user input and database questions → compute cosine similarity

#### 📌 Pass-Strategy Algorithm

* **Formula**:
  `Strategic Value = Topic Frequency × Average Marks Per Appearance`
* **Mechanism**:

  * Calculate user’s deficit
  * Rank unstudied topics by Strategic Value
  * Recommend highest ROI topics until gap is closed

#### 📌 Monte Carlo Simulation

* Generate 100,000 simulated papers
* For each:

  * Roll for topic appearance (based on historical probability)
  * Assign random historical mark value
  * Tally up if student would pass
* **Output**: Pass probability = % of simulations ≥ target score

---

### 📘 Component 2: RAG Knowledge Engine (`RAGAnalyzer`)

#### 💡 Pipeline Overview

1. **Load & Split**:
   Parse PDFs → Chunk with overlap using `RecursiveCharacterTextSplitter`

2. **Embed & Store**:
   Use `embedding-001` → Store in `ChromaDB`

3. **Retrieve**:
   Query embedded → Retrieve top chunks with vector similarity

4. **Generate**:
   Use `Gemini 1.5 Flash` to answer based only on relevant context

> ✳️ This grounds the LLM’s answers, reducing hallucination.

---

## 🖼️ Screenshots

> <img width="1879" height="1062" alt="image" src="https://github.com/user-attachments/assets/1116d383-afe4-46e7-9018-e7cc1800667c" />


* **Main Dashboard**
  <img width="1888" height="1045" alt="image" src="https://github.com/user-attachments/assets/46efc06b-546e-478d-bf14-87ef9c4628cb" />


* **Pass Strategy View**
  <img width="1867" height="1056" alt="image" src="https://github.com/user-attachments/assets/aade3cd7-8895-47d0-85c3-1641d8ae051f" />


* **RAG Chat Interface**
  <img width="1889" height="1055" alt="image" src="https://github.com/user-attachments/assets/7f8fe0b0-dd62-4ca4-b2c3-9e5d0562e7da" />


---


## 👩‍💻 Team Contributions

* **Anagha K** – Frontend Lead
  Built the entire React frontend with Vite, TypeScript, TailwindCSS, and Shadcn/UI.

* **Saurav Sreejith** – Backend & Algorithms
  Built the Flask API, semantic search engine, strategic value algorithm, and Monte Carlo simulator.

* **Shreya Padmakumar** – Team Lead, UI & Documentation
  Handled the comprehensive documentation of the project and assisted with frontend design

* **S Murugan** –  AI & RAG Specialist
  Designed the RAGAnalyzer pipeline using LangChain, Gemini, ChromaDB, and PDF processing. Handled DevOps & Architecture
  


