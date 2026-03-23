# Expense Categorizer

An AI-powered web application that automatically categorises bank transactions using NLP and Machine Learning. Upload your bank statement (CSV, Excel or PDF) and get instant spending insights with confidence scores per transaction.

---

## What it does

- Accepts bank statements in **CSV, Excel (.xlsx) or PDF** format
- Runs every transaction description through an **NLP pipeline** — cleaning, embedding and classification
- Predicts one of **8 spending categories** per transaction: Food, Groceries, Transport, Bills, Shopping, Entertainment, Health, Income
- Returns a **confidence score** (0–1) per prediction so you know which ones to trust
- Renders an **analytics dashboard** with category breakdown, account analysis and confidence distribution
- On return visits, **re-runs the pipeline from your saved file** — no need to re-upload

---

## ML Pipeline

```
Raw transaction description
        ↓
Text preprocessing (lowercase, remove punctuation, stopword removal)
        ↓
Sentence embeddings — all-MiniLM-L6-v2 (384 dimensions)
        ↓
Amount feature — log1p → StandardScaler → 1 dimension
        ↓
Feature matrix — hstack embeddings + scaled amount (385 dimensions)
        ↓
RandomForestClassifier (100 trees, max_depth=20)
        ↓
Predicted category + confidence score per transaction
```

**Training accuracy: 87% across 8 balanced categories on 8,000 labelled transactions**

---

## Tech Stack

| Layer | Technology |
|---|---|
| ML / NLP | sentence-transformers, scikit-learn, pandas, pdfplumber |
| Backend | FastAPI, SQLAlchemy, PostgreSQL, Alembic |
| Frontend | Jinja2 templates, Bootstrap 5, Chart.js |
| Auth | JWT (httpOnly cookies), bcrypt password hashing |
| Deployment | Docker |

---

## Project Structure

```
expense-categorizer/
├── main.py                  # FastAPI app entry point
├── config.py                # Environment variable management
├── requirements.txt
├── Dockerfile
│
├── api/                     # JSON API endpoints
│   ├── auth.py              # register, login, logout, /me
│   ├── upload.py            # file upload + preview
│   ├── predict.py           # ML pipeline trigger
│   └── dashboard.py        # return visit data fetch
│
├── pages/                   # HTML page routes (Jinja2)
│   ├── home.py
│   ├── auth_pages.py
│   ├── upload_pages.py
│   └── dashboard_pages.py
│
├── ml/                      # All ML/NLP code
│   ├── preprocessor.py      # text cleaning
│   ├── embedder.py          # sentence-transformers wrapper
│   ├── file_parser.py       # CSV, Excel, PDF parsers
│   ├── train_pipeline.py    # offline training script
│   ├── predict_pipeline.py  # inference pipeline
│   └── artefacts/           # saved model, scaler, label encoder
│
├── db/
│   ├── database.py          # SQLAlchemy engine + session
│   ├── models.py            # User, UploadedFile ORM models
│   └── migrations/          # Alembic migration files
│
├── schemas/                 # Pydantic request/response models
├── utils/                   # JWT, hashing, file utils, page auth
├── templates/               # Jinja2 HTML templates
└── static/                  # CSS and JavaScript files
```

---

## Setup & Installation

### Prerequisites

- Python 3.10+
- PostgreSQL
- Git

### 1. Clone the repository

```bash
git clone https://github.com/your-username/expense-categorizer.git
cd expense-categorizer
```

### 2. Create virtual environment

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file at the project root:

```
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/expense_db
SECRET_KEY=your-very-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
UPLOAD_DIR=uploads
```

### 5. Create the database

Create a PostgreSQL database named `expense_db`, then run migrations:

```bash
alembic upgrade head
```

### 6. Train the model

Place your labelled dataset (CSV with `description`, `amount`, `category` columns) in `data/`:

```bash
python -m ml.train_pipeline
```

This saves `model.pkl`, `scaler.pkl` and `label_encoder.pkl` to `ml/artefacts/`.

### 7. Run the application

```bash
uvicorn main:app --reload --port 8080
```

Visit `http://localhost:8080`

---

## API Endpoints

| Method | Endpoint | Description | Auth required |
|---|---|---|---|
| POST | /api/register | Register new user | No |
| POST | /api/login | Login, sets JWT cookie | No |
| GET | /api/logout | Logout, clears cookie | No |
| GET | /api/me | Get current user | Yes |
| POST | /api/upload | Upload CSV/Excel/PDF | Yes |
| GET | /api/preview/{file_id} | Preview parsed rows | Yes |
| POST | /api/predict | Run ML pipeline | Yes |
| GET | /api/dashboard/data | Fetch saved analysis | Yes |

---

## Key Design Decisions

**No predictions stored in DB** — The uploaded file is the source of truth. The ML pipeline re-runs on return visits from the saved file. This keeps the database lean — only `users` and `uploaded_files` tables exist.

**Optimistic UI** — After prediction, results are stored in `sessionStorage` and the dashboard renders immediately. No waiting for background operations.

**Same preprocessing in train and predict** — `preprocessor.py` and `embedder.py` are imported by both pipelines. Same cleaning logic, same scaler (`.transform()` only at inference, never `.fit_transform()`). This prevents the most common production ML bug.

**Lazy model loading** — The sentence-transformers model loads on first prediction request, not at app startup. This keeps startup time fast and the health check endpoint responsive.

---

## Supported File Formats

| Format | Parser | Notes |
|---|---|---|
| CSV | pandas `read_csv()` | Requires `description`, `amount` columns |
| Excel (.xlsx) | pandas `read_excel()` + openpyxl | Same column requirements |
| PDF | pdfplumber | Extracts tables from bank statement PDFs |

`account_number` column is optional — defaults to `N/A` if not present.

---

## Categories

The model is trained to classify transactions into 8 categories:

`Food` · `Groceries` · `Transport` · `Bills` · `Shopping` · `Entertainment` · `Health` · `Income`

---

## License

MIT
