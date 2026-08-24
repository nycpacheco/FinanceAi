# 💸 FinanceAI - Smart Financial Manager

A personal finance manager that uses Artificial Intelligence (Google Gemini) to record, interpret, and categorize your expenses automatically through plain text.

> **Note:** Since the backend is hosted on Render's free tier, the server goes into sleep mode when inactive. Please allow about 50 seconds for the server to spin up on your first request!

🌍 **Access the project online:** [Click here to access FinanceAI](https://finance-ai-pi-six.vercel.app/)

![FinanceAI Preview](./assets/preview.png)

---

## 🚀 Technologies Used

**Frontend:**
* HTML5, CSS3 & vanilla JavaScript
* [Tailwind CSS](https://tailwindcss.com/) (via CDN for fast styling)
* Hosting: [Vercel](https://vercel.com/)

**Backend:**
* [Python 3.10+](https://www.python.org/)
* [FastAPI](https://fastapi.tiangolo.com/) (API and routes creation)
* [SQLAlchemy](https://www.sqlalchemy.org/) + SQLite (Database)
* AI Integration: Google Gemini API
* Hosting: [Render](https://render.com/)

---

## ✨ Features

* **AI Recording:** Type "I spent 50 at the grocery store today" and the AI automatically categorizes it, extracts the amount, and saves it.
* **Dynamic Dashboard:** Real-time visualization of income, expenses, and current balance.
* **50-30-20 Rule:** Smart financial health analysis based on your goals.
* **Transaction Management:** Quick deletion of transactions with instant interface updates.

---
## 📖 How to Use the Application

The FinanceAI workflow was designed to be simple and direct, focusing on the user experience:

**1. Initial Setup (Goals)**
* When accessing it for the first time, the system will ask you to set your spending goals for different categories (Fixed Expenses, Variable Expenses, etc.).
* These values will serve as the basis for the artificial intelligence to calculate your financial health.

**2. Inserting Transactions with AI**
* In the main text field, you don't need to fill out boring forms. Just type as if you were sending a message.
* *Examples of what you can type:* 
  * "I received a 3500 salary today"
  * "I spent 150 at the grocery store"
  * "I paid 80 bucks for the internet"
* The AI will read it, identify the correct category, extract the monetary value, and save it in the database.

**3. Feedback and Alerts**
* Every time you add an expense, the AI analyzes its impact on your budget. 
* It can return warning alerts (e.g., if you are exceeding your Variable Expenses goal) or encouraging messages if you are saving well.

**4. Tracking (Dashboard)**
* The main screen displays real-time calculations based on the **50-30-20 Rule** (Needs, Wants, and Savings).
* You can view your entire history and, if the AI gets the category wrong or you cancel a purchase, just click the trash icon to instantly delete the record.

---

## 📋 Prerequisites (Requirements)

To run this project locally, you will need:
* Python 3.10 or higher installed.
* A free API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
* Git installed on your machine.

---

## 🔧 How to Run Locally

**1. Clone the repository:**
```bash
git clone [https://github.com/nycpacheco/FinanceAi.git](https://github.com/nycpacheco/FinanceAi.git)
cd FinanceAi
```

**2. Create and activate a virtual environment (Optional, but recommended):**
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

**3. Install backend dependencies:**
```bash
pip install -r requirements.txt
```

**4. Configure Environment Variables:**
Create a `.env` file in the root of the project and add your Gemini API key:
```env
GEMINI_API_KEY=your_key_here
```

**5. Start the local server:**
```bash
uvicorn src.main:app --reload
```
The API will be running at `http://localhost:8000`.

**6. Running the Frontend:**
Since the frontend is static (HTML/JS), just open the `index.html` file directly in your browser or use the *Live Server* extension in VS Code. (Remember to change the fetch URL in JS back to `localhost:8000` for local testing).

---

## ✒️ Author

Developed by **Nycolas Pacheco**!

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/nycpacheco/)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/nycpacheco)
