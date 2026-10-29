# Disaster AI — Intelligent Disaster Prediction and Emergency Response Platform

![Disaster AI Platform](https://img.shields.io/badge/Status-Operational-emerald?style=for-the-badge)
![Tech Stack](https://img.shields.io/badge/Stack-React_18_|_Flask_3_|_Scikit--Learn-0284C7?style=for-the-badge)
![Geospatial](https://img.shields.io/badge/Mapping-Leaflet_|_OpenStreetMap-F97316?style=for-the-badge)
![Domain Focus](https://img.shields.io/badge/Hazards-Floods_&_Landslides_(India)-EF4444?style=for-the-badge)

> **IMPORTANT SCIENTIFIC & ETHICAL DISCLAIMER:**
> **Disaster AI** is an emergency decision-support, situational awareness, and demonstration platform. It is not an officially certified meteorological early-warning authority (such as IMD or CWC). Output hazard scores and simulated predictions are decision-support estimates engineered for emergency planning and human-in-the-loop operational validation.

---

## 1. Executive Summary & Architecture

**Disaster AI** is an AI-powered disaster intelligence and emergency response platform tailored to support disaster management authorities, rescue battalions (NDRF/SDRF), and citizens. The system addresses the complete disaster lifecycle:
1. **Predictive Hazard Risk Modeling**: Evaluates hydro-geological physics features (slope angle, rainfall saturation, soil moisture, river proximity) using Scikit-Learn.
2. **Citizen Emergency Crowdsourcing**: Real-time reporting with GPS map location pinning, impact metrics, and photo uploads.
3. **NLP-Based Triage & Prioritization**: Multi-criteria explainable human safety index ranking life threat (trapped, injured) with zero demographic bias.
4. **Common Operating Picture (COP)**: Interactive Leaflet geospatial map with hazard overlays, shelter capacities, and unit tracking.
5. **Tactical Rescue Dispatch**: Mission lifecycle tracking (`Assigned` &rarr; `En Route` &rarr; `On Site` &rarr; `Resolved`).
6. **Bilingual Public Warnings**: Emergency alerts in **English and Hindi (हिंदी)** with browser Text-to-Speech synthesis.
7. **Fine-Tuned LLM Citizen Safety Assistant**: Dedicated bilingual conversational AI for disaster survival, first aid, evacuation, and shelter inquiry trained on verified NDMA & NDRF protocols via PEFT LoRA (Strictly RAG-free).

```
disaster-ai/
├── backend/
│   ├── app/
│   │   ├── config.py             # Secrets, DB URI, file limits
│   │   ├── database.py           # SQLAlchemy ORM
│   │   ├── models/               # User, Incident, Risk, Rescue, Shelter, Alert
│   │   ├── assistant/            # Safety guard & LLM engine loader
│   │   │   ├── safety_guard.py   # Multi-tier peril detection & 112 routing
│   │   │   └── llm_engine.py     # Qwen2.5 LoRA loader & bilingual NDMA fallback
│   │   ├── ml/                   # Scikit-Learn Hazard Engine & NLP Triage
│   │   │   ├── hazard_risk_model.py
│   │   │   ├── nlp_classifier.py
│   │   │   └── prioritization_engine.py
│   │   ├── data_providers/       # IMD weather, terrain elevation, satellite CV
│   │   ├── routes/               # REST API blueprints (including /api/assistant)
│   │   ├── schemas/              # Pydantic request validators
│   │   └── utils/                # JWT and Role-Based Access Control (RBAC)
│   ├── tests/                    # Automated unit tests (13 test suites)
│   ├── seed_data.py              # Realistic Indian scenario seed script
│   ├── run.py                    # Server launch script (Port 5000)
│   └── requirements.txt
├── training/                     # Fine-Tuning Pipeline (LoRA / SFT)
│   ├── prepare_dataset.py        # Curated bilingual NDMA/NDRF dataset builder
│   ├── train_sft.py              # HuggingFace TRL + PEFT LoRA trainer
│   ├── inference.py              # Standalone CLI inference tester
│   ├── evaluate_model.py         # Held-out benchmark test evaluator
│   ├── config.yaml               # Model & LoRA hyperparameters
│   └── DisasterAI_FineTuning_Colab.ipynb # Ready-to-run Google Colab T4 GPU notebook
├── data/                         # Curated Dataset Splits
│   ├── train.jsonl               # 22 SFT training dialogues (English, Hindi, Hinglish)
│   ├── validation.jsonl          # 2 validation dialogues
│   ├── test.jsonl                # 3 held-out evaluation dialogues
│   └── dataset_manifest.json     # Statistics & protocol verification citations
├── models/                       # LoRA Adapter Weights & Registry
│   ├── README.md                 # Model provenance & licensing documentation
│   └── evaluation_results.json   # Quantitative safety metrics report
├── frontend/
│   ├── src/
│   │   ├── components/           # LeafletMap, LocationPicker, Badges, AudioTTS
│   │   ├── contexts/             # AuthContext, LanguageContext (Bilingual)
│   │   ├── pages/                # 11 dedicated responsive views (including AssistantPage)
│   │   ├── services/             # API clients (including assistantService)
│   │   └── types/                # TypeScript interfaces
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
├── README.md
└── .env.example
```

---

## 2. Default Demo User Accounts

The database comes pre-seeded with three operational role accounts:

| Role | Username | Password | Operational Capabilities |
| :--- | :--- | :--- | :--- |
| **Disaster Administrator** | `admin` | `AdminPass123!` | Incident verification, AI priority override, tactical unit dispatch, bilingual alert broadcast, full analytics |
| **Rescue Team Officer** | `rescue_lead` | `RescuePass123!` | Field mission log, status updates (`En Route`, `On Site`, `Resolved`), equipment request |
| **Citizen Reporter** | `citizen` | `CitizenPass123!` | Incident reporting, GPS pin placement, view personal status, public safety tips |

*Note: Quick 1-click test credentials buttons are available directly on the login screen.*

---

## 3. Quickstart & Installation (Windows / PowerShell)

### Prerequisites
- Python 3.10+ (Tested on Python 3.14.6)
- Node.js 18+ (Tested on v24.20.0) & npm

### Step 1: Clone or Navigate to the Workspace
```powershell
cd c:\Users\ADMIN\Downloads\GeoNexis
```

### Step 2: Backend Setup
1. Open PowerShell and navigate to `backend`:
   ```powershell
   cd backend
   ```
2. (Optional) Create and activate a Python virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
3. Install backend dependencies:
   ```powershell
   python -m pip install -r requirements.txt
   ```
4. Seed the database with realistic demonstration scenarios:
   ```powershell
   python seed_data.py
   ```
5. Launch the Flask backend server:
   ```powershell
   python run.py
   ```
   *The server will start on `http://localhost:5000`.*

### Step 3: Frontend Setup
1. Open a second PowerShell window and navigate to `frontend`:
   ```powershell
   cd c:\Users\ADMIN\Downloads\GeoNexis\frontend
   ```
2. Install frontend dependencies:
   ```powershell
   npm.cmd install
   ```
3. Launch the Vite development server:
   ```powershell
   npm.cmd run dev
   ```
   *The client application will start on `http://localhost:5173`.*

---

## 4. Implemented Pages (11 Views)

1. **Landing Page (`/`)**: Real-time operational ticker, active emergency alert ticker, feature cards, AI assistant quick-launch, and regional risk hotspot cards.
2. **Login & Registration (`/login`, `/register`)**: Role-based authentication with 1-click test login presets.
3. **Disaster AI Citizen Safety Assistant (`/assistant`)**: Dedicated full-page conversational AI console featuring voice speech-to-text (STT), text-to-speech (TTS), suggested bilingual emergency prompt chips, instant life-peril detection, 112/1078 helpline banners, and transparent fine-tuned model provenance badges.
4. **Citizen Dashboard (`/citizen`)**: Personal incident tracking, response lifecycle, AI assistant banner, national emergency helplines (112, 1078, 108), and bilingual Do's and Don'ts.
5. **Emergency Report Submission (`/report`)**: Geospatial interactive Leaflet location pin picker, casualty/trapped counters, checklist of critical needs, and immediate AI urgency assessment modal.
6. **Disaster Administrator Operations Console (`/admin`)**: Operational command dashboard with KPI metrics, unverified queue triage, quick verification/rejection, and rescue team dispatch modal.
7. **Interactive Disaster Geospatial Map (`/map`)**: Full-screen Leaflet map with OpenStreetMap tiles, layer toggles (Incidents, Risk Zones, Shelters, Rescue Units), jump-to-hotspot buttons, and sidebar incident inspector.
8. **Incident Details & Verification Console (`/incidents/:id`)**: Transparent factor-by-factor AI prioritization breakdown table, operator priority override, and unit mobilization.
9. **Rescue Team Dashboard (`/rescue`)**: Active missions view, field progress updater (`Assigned` &rarr; `En Route` &rarr; `On Site` &rarr; `Resolved`), operational obstacles logger, and straight-line road safety caution banner.
10. **Emergency Alerts & Warnings (`/alerts`)**: Multilingual (English/Hindi) broadcast feed, browser Web Speech Text-to-Speech audio readout, and administrative alert creation form.
11. **Analytics & Performance (`/analytics`)**: Recharts visualizations derived from live database metrics (7-day trend timeline, priority distribution pie chart, hazard bar chart, triage verification efficiency).

---

## 5. AI/ML Engineering & Explainability

### Hazard Risk Engine (`app/ml/hazard_risk_model.py`)
- **Estimators**: Scikit-Learn `RandomForestClassifier` (hazard category) + `GradientBoostingRegressor` (continuous 0-100 hazard score).
- **Domain Physical Consistency**:
  - **Floods**: Models high recent (48h) + forecast (24h) rainfall, high soil moisture saturation, proximity to river channels (&lt;2 km), low elevation, and drainage density.
  - **Landslides**: Models steep slope angles (&gt;25°), monsoon infiltration accumulation, elevated pore-water pressure, and mountainous elevations.
- **Explainability**: Quantifies factor-by-factor contributions (e.g. `Critically Steep Slope (+38°)` or `Extreme Recent Rainfall (+210mm)`).
- **Imputation & Fallback**: Automatically fills missing parameters using regional geoclimatic defaults while returning explicit warnings to the caller.

### NLP Incident Triage & Duplicate Detection (`app/ml/nlp_classifier.py`)
- Extracts critical emergency keywords across 6 peril taxonomies (trapped, medical, rising water, structural damage, mudflow, critical supplies).
- Evaluates spatial proximity (&lt;3km) combined with TF-IDF cosine similarity to cluster duplicate citizen reports.

### Multi-Criteria Explainable Prioritization (`app/ml/prioritization_engine.py`)
- Calculates a transparent human safety score ($0-100$ pts):
  - **Trapped Individuals**: Up to 35 pts (highest peril weight)
  - **Casualties & Urgent Medical**: Up to 25 pts
  - **Affected Population Scale**: Up to 15 pts
  - **Evacuation & Sustenance Isolation**: Up to 15 pts
  - **Critical NLP Keyword Escalation**: Up to 10 pts
- **Ethical Safeguard**: Strict human-in-the-loop decision-support. Automated scoring serves as advisory assistance; final rescue dispatches are verified by duty officers.

### Fine-Tuned LLM Citizen Assistant (`training/`, `backend/app/assistant/`)
- **Base LLM Architecture**: `Qwen/Qwen2.5-0.5B-Instruct` (Apache 2.0). ~490M parameters selected for fast CPU/edge inference latency, native Hindi/English tokenization, and rapid GPU fine-tuning.
- **Supervised Fine-Tuning (SFT) & LoRA Pipeline**:
  - Training script: `training/train_sft.py` utilizing Hugging Face `TRL` (`SFTTrainer`) + `PEFT` LoRA.
  - LoRA Hyperparameters: Rank $r=16$, $\alpha=32$, dropout $0.05$, target modules (`q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj`).
  - 4-bit NormalFloat (NF4) QLoRA supported on CUDA GPUs; float32/fp16 LoRA on CPU.
- **Strict RAG-Free Architecture**:
  - Zero vector databases, embeddings, ChromaDB, or Pinecone at inference time.
  - Disaster survival principles and official protocols reside directly in the model's fine-tuned neural weights.
  - Real-time contextual parameters (active local warnings and open shelter occupancies) are injected directly into the chat prompt from live SQLite database models (`Shelter` and `Alert`) when citizens ask location-specific questions.
- **Curated Dataset Provenance**:
  - 27 high-priority disaster survival scenarios cross-verified against official Indian disaster authorities:
    1. **NDMA SACHET Do's & Don'ts**: https://sachet.ndma.gov.in/DosDont
    2. **NDRF Disaster Awareness**: https://ndrf.gov.in/en/disaster-awareness
    3. **NDRF Basic Disaster Management Course**: https://ndrf.gov.in/en/basic-disaster-management-course
  - Grouped split preventing scenario leakage: `data/train.jsonl` (22 examples), `data/validation.jsonl` (2 examples), `data/test.jsonl` (3 examples).
  - Languages covered: English, Hindi (Devanagari), and conversational Hinglish across 9 disaster types (Floods, Earthquakes, Cyclones, Landslides, Building Fires, Heatwaves, Tsunami, First Aid/Severe Bleeding, Emergency 72-Hour Kits).
- **Google Colab T4 GPU Notebook (`training/DisasterAI_FineTuning_Colab.ipynb`)**:
  - Complete, self-contained notebook enabling 1-click cloud fine-tuning on a free Google Colab T4 GPU.
  - Exports trained LoRA adapter weights directly into `models/disaster_ai_qwen_lora/` with automated zip packaging.
- **Dual-Tier Emergency Safety Guard (`app/assistant/safety_guard.py`)**:
  - Independent safety interceptor running synchronously before and alongside LLM generation.
  - Detects immediate life-threatening peril (rising water entering homes, building shaking/cracking, active fires, severe arterial bleeding).
  - Enforces rapid, non-hallucinated survival directives and prominently surfaces National Emergency Helpline **112**, NDRF **1078**, Ambulance **108**, and Fire **101**.
- **Transparent Provenance & Fallback**:
  - Inspects whether fine-tuned LoRA weights (`models/disaster_ai_qwen_lora/adapter_config.json`) or pretrained base model weights are active.
  - When the neural network is initializing in the background, a non-blocking verified NDMA protocol safety baseline responds with zero latency, ensuring citizens in distress never encounter an unresponsive or freezing interface.

---

## 6. REST API Documentation

### Citizen AI Assistant (`/api/assistant`)
- `POST /api/assistant/chat` — Conversational disaster safety guidance. Evaluates queries with emergency safety guard, injects live local shelter/alert context, queries the fine-tuned LLM, and returns verified advice with model metadata and helpline recommendations.
- `GET /api/assistant/health` — Assistant service health, active device (`cpu` / `cuda`), base model name, and fine-tuned status flag.
- `GET /api/assistant/model-info` — Detailed architectural provenance, LoRA configuration, official NDMA/NDRF citations, and RAG-free architecture confirmation.

### Authentication (`/api/auth`)
- `POST /api/auth/register` — Register a new user (`citizen`, `rescue_team`, or `admin`).
- `POST /api/auth/login` — Authenticate and receive a 24-hour signed JWT token.
- `GET /api/auth/me` — Retrieve current authenticated user profile.

### Incident Management (`/api/incidents`)
- `POST /api/incidents` — Submit emergency report. Runs NLP keyword extraction, duplicate clustering, and prioritization scoring.
- `GET /api/incidents` — Filter and paginate incidents by hazard, priority, status, and verification state.
- `GET /api/incidents/<id>` — Retrieve detailed incident record with full explainability factors.
- `POST /api/incidents/<id>/verify` — *(Admin Only)* Set verification status (`verified`, `rejected`, `duplicate`, `needs_info`) and optional priority override.
- `PATCH /api/incidents/<id>/status` — *(Admin / Rescue Team)* Update operational lifecycle status.
- `POST /api/incidents/upload-image` — Upload incident scene photo.

### AI Risk Engine (`/api/risk`)
- `POST /api/risk/predict` — Execute Scikit-Learn hazard engine; returns risk category, score, explainability factors, and model provenance.
- `GET /api/risk/history` — Query past assessments stored in database.
- `GET /api/risk/areas` — Retrieve monitored Indian disaster hotspots (Wayanad, Kaziranga, Joshimath, Mumbai).

### Emergency Alerts (`/api/alerts`)
- `GET /api/alerts` — Fetch active bilingual advisories.
- `POST /api/alerts` — *(Admin Only)* Broadcast bilingual warning in English and Hindi.
- `DELETE /api/alerts/<id>` — *(Admin Only)* Deactivate alert.

### Rescue Operations (`/api/rescue`)
- `GET /api/rescue/teams` — List registered rescue battalions and deployment availability.
- `POST /api/rescue/assign` — *(Admin Only)* Mobilize rescue team to verified incident.
- `GET /api/rescue/assignments` — Retrieve mission dispatches.
- `PATCH /api/rescue/assignments/<id>/status` — Update field progress (`Assigned`, `En Route`, `On Site`, `Resolved`) and log resource needs.

### Relief Shelters (`/api/shelters`)
- `GET /api/shelters` — List evacuation shelters, capacities, and resource inventories.
- `PATCH /api/shelters/<id>/occupancy` — Update current bed occupancy.

### Operations Analytics (`/api/analytics`)
- `GET /api/analytics/overview` — Aggregated operational statistics for Recharts dashboards.

---

## 7. Automated Testing Results

The backend includes a comprehensive automated test suite covering authentication, RBAC guards, incident creation, Scikit-Learn risk inference, missing-data imputation, NLP triage, emergency safety guard, and assistant chat API contracts.

Run tests:
```powershell
cd backend
python -m unittest discover -s tests -p "test_*.py"
```

**Test Execution Output:**
```
Ran 13 tests in 2.643s
OK (All 13 tests passing)
```

---

## 8. Known Limitations & Roadmap

- **Simulated Environmental Baseline**: Real-time production operation requires continuous ingestion from IMD radar grids and Central Water Commission telemetry via authenticated government API gateways.
- **Satellite Damage Assessment**: The included satellite change module provides an analytical change-detection interface; production deployment requires cloud-free Sentinel-1 SAR GRD access and GPU inference nodes.
- **Routing**: Current map links show approximate spatial positions; tactical turn-by-turn routing during floods requires dynamic road-inundation vector graphs from state highway authorities.
