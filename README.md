# 🧠 Chat with Your Notes — Advanced AI Document Q&A System

A powerful, feature‑rich web application that lets users upload, manage, and query documents using AI. Built with **Python** and **Streamlit**, leveraging **HuggingFace** models for intelligent question‑answering.

---

## 🌈 Highlights

### 🧩 Core Capabilities

* **🤖 AI‑Powered Q&A** — Ask natural‑language questions and get precise answers from your documents
* **📄 Multi‑Format Uploads** — Supports PDF and TXT files
* **🗃️ Persistent Library** — Documents stored locally and tracked via SQLite
* **🧵 Context‑Aware Chat** — Maintains conversation context across follow‑ups

---

## 🗂️ Document Management

* **📥 Bulk Uploads** — Drag & drop multiple PDFs and text files
* **📚 Central Library** — View all uploaded documents in one place
* **🔎 Smart Search** — Find files instantly by name
* **👀 Preview Mode** — Inspect file contents before processing
* **🧹 Selective Delete** — Remove individual documents
* **🗑️ One‑Click Cleanup** — Clear the entire library
* **📤 Export List** — Download the document inventory

---

## 💬 Chat Experience

* **🕘 Recent History** — Displays the last 5 Q&A pairs
* **💡 Quick Prompts** — One‑tap question templates
* **📋 Copy Answers** — Copy AI responses instantly
* **🧾 Export Chats** — Download full conversations as TXT
* **💾 Persistent Logs** — Chat history saved automatically

---

## 📊 Insights & Metrics

* **🔢 Document Count** — Total files uploaded
* **💽 Storage Usage** — Track space consumed
* **⏱️ Timestamps** — See when each document was added

---

## 🎛️ User Experience

* **🧭 Intuitive Navigation** — Clean sidebar layout
* **⏳ Progress Feedback** — Visual indicators during processing
* **📱 Responsive UI** — Works on desktop and mobile
* **🧩 Icon‑Led Actions** — Clear cues for every feature
* **🛈 Inline Help** — Tooltips where you need them

---

## 🧰 Tech Stack

* **🎨 Frontend** — Streamlit
* **⚙️ Backend** — Python
* **🧠 AI/ML** — HuggingFace Inference API

  * Embeddings: `sentence-transformers/all-MiniLM-L6-v2`
  * LLM: `google/flan-t5-xxl`
* **🗄️ Database** — SQLite
* **📐 Vector Search** — Custom cosine similarity

---

## 🚀 Getting Started

1. **📦 Clone the repo**

   ```bash
   git clone <your-repo-url>
   cd AskMyNotes
   ```

2. **📥 Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **🔑 Create a HuggingFace token**

   * Visit HuggingFace → Settings → Tokens
   * Generate a token (Read access)

4. **▶️ Run the app**

   ```bash
   streamlit run app.py
   ```

5. **🌐 Open in browser**

   * Go to `http://localhost:8501`
   * Paste your HuggingFace token
   * Upload documents and start asking!

---

## 🧭 How It Works

### 1️⃣ Upload

* Add PDFs or TXT files to your library

### 2️⃣ Process (One‑Time)

* Click **⚡ Process Library**
* Embeddings are generated and cached

### 3️⃣ Ask

* Type questions or use quick prompts
* Get fast, accurate answers

### 4️⃣ Reuse

* Restart the app — instant load from cache
* Repeated questions return even faster

---

## 🎯 Who It’s For

* **🎓 Students** — Notes, textbooks, research
* **💼 Professionals** — Reports, manuals, policies
* **🔬 Researchers** — Papers, reviews, datasets
* **✍️ Writers** — References, drafts
* **👤 Anyone** — Personal knowledge bases

---

## 🔐 Privacy First

* Processing is local or via HuggingFace API
* No external data storage
* Files remain on your machine
* API tokens are session‑only

---

## 🧠 Power Features

### ⚡ Quick Prompts

* “Summarize the main points”
* “Key takeaways?”
* “Explain simply”
* “Important dates?”

### 📈 Live Stats

* File count
* Storage size (MB)

### 🔍 Instant Search

* Case‑insensitive
* Real‑time filtering

### 🗃️ History Controls

* Auto‑saved chats
* Last 5 Q&A shown
* Export full history

---

## 🤝 Contributing

* 🐞 Report bugs
* 💡 Suggest features
* 🔧 Submit PRs

---

## 📜 License

MIT License

---

## 🙌 Credits

* Streamlit
* HuggingFace
* PyPDF2

---

**Crafted with ✨ for smarter document understanding**
