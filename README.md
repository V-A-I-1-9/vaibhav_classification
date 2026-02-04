# PO Category Classification System

## 📌 Project Overview
This project is an AI-powered Purchase Order (PO) classification system that
automatically categorizes PO descriptions into predefined business categories
(L1, L2, L3) using a Large Language Model (LLM).

The system is designed to reduce manual effort in enterprise finance and
procurement workflows.

---

## 🌐 Live Demo
🚀 **Streamlit App:**  
https://<your-streamlit-app-url>

---

## 🧠 Key Features
- Multi-level PO classification (L1, L2, L3)
- Fixed enterprise taxonomy
- Few-shot prompt engineering
- Deterministic AI output (temperature = 0)
- Structured JSON responses
- Interactive Streamlit frontend

---

## 🏗️ Tech Stack
- Python
- Streamlit
- Groq API
- Large Language Models (LLMs)
- Prompt Engineering

---

## 📂 Project Structure
vaibhav_classification/
│
├── app.py # Streamlit frontend
├── classifier.py # PO classification logic
├── prompts.py # Prompt templates
├── taxonomy.py # Business taxonomy
├── requirements.txt # Dependencies
├── README.md
├── .gitignore

---

## 🚀 How to Run Locally

### 1️⃣ Install dependencies
~~~bash
pip install -r requirements.txt
~~~

### 2️⃣ Set API key
Create:

~~~text
.streamlit/secrets.toml
~~~

Add:

~~~toml
GROQ_API_KEY = "your_api_key_here"
~~~

### 3️⃣ Run the app
~~~bash
streamlit run app.py
~~~

---

## 🧪 Example Use Cases

- Automating PO classification in finance teams  
- Categorizing IT, HR, and T&E expenses  
- Reducing manual data entry in procurement workflows  

---

## 🧠 Concepts Used

- Prompt Engineering  
- Few-shot Learning  
- Taxonomy-based Classification  
- Generative AI for Enterprise Applications  

---

## 👤 Author

Vaibhav

