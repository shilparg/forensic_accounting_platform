This is the final touch. A world-class data engineering project deserves a world-class `README.md`. 

When the grading panel (or a future employer) lands on your GitHub repository, this document will immediately signal that this is a professional, production-ready enterprise platform, not just a student script.

Copy this Markdown text exactly as it is and paste it into a file named **`README.md`** in your root folder.

***

```markdown
# 🕵️‍♂️ AI-Driven Forensic Accounting Platform

An automated, end-to-end Modern Data Stack designed to detect financial obfuscation, narrative drift, and market triangulation anomalies in public company disclosures.

**Developed by:** Kamlesh & Shilpa  
**Program:** NTU SCTP Capstone Project  

---

## 📖 Project Overview
Traditional forensic auditing relies heavily on manual document review and historical numerical analysis, often creating a "blind spot" regarding management tone and real-time market pressure. 

This platform modernizes the audit process by ingesting raw SEC 10-K filings, quantifying the linguistic features of the disclosures, and using unsupervised Machine Learning to cross-reference internal management sentiment against external market data (Yahoo Finance). 

When a "Critical Anomaly" is detected, the platform automatically generates an executive risk summary using Generative AI (Google Gemini) and dispatches it to the audit team.

---

## ✨ Key Features & Forensic Methodologies

* **The Obfuscation Hypothesis:** Correlates 10-K word counts (Disclosure Density) with Management Sentiment to identify companies hiding bad news in boilerplate text.
* **Market Triangulation:** Bridges internal SEC data with external market metrics (Short Ratio, Debt-to-Equity) to find "Smoking Gun" disconnects.
* **Narrative Drift (Reporting Inertia):** Utilizes TF-IDF Cosine Similarity to track year-over-year changes in 10-K language, pinpointing the exact fiscal year management drastically rewrites their financial story.
* **Unsupervised Anomaly Detection:** Employs an Isolation Forest algorithm to score and categorize peer-group outliers without human bias.
* **Gen-AI Executive Alerting:** Integrates Google Gemini 1.5 Flash to synthesize complex anomaly data into a 3-bullet-point, human-readable email alert for Audit Partners.

---

## 🏗️ Architecture & Tech Stack

This project is built on a highly fault-tolerant, automated pipeline:

1. **Orchestration:** `Dagster`
2. **Extraction:** `Python`, `BeautifulSoup`, `SEC EDGAR API`, `yfinance`
3. **Landing Zone:** `MongoDB`
4. **Data Warehouse:** `Google Cloud BigQuery`
5. **Transformation:** `dbt` (Data Build Tool)
6. **Machine Learning:** `Scikit-Learn` (Isolation Forest), `TextBlob` (NLP)
7. **Visualization & AI:** `Seaborn`, `Matplotlib`, `Google Generative AI`

---

## 📂 Repository Structure

```text
forensic_accounting_platform/
├── orchestrate/                     
│   └── assets.py                     # Master Dagster Orchestrator
├── extract_load/                    
│   ├── cleanup_mongo.py              # Landing zone sanitizer
│   ├── extract_sec_data.py           # SEC API Scraper & NLP Parser
│   ├── verify_mongo.py               # Data Quality Gate
│   └── mongo_to_bigquery.py          # GCP Cloud Sync
├── transform_dbt/                   
│   └── models/
│       ├── staging/stg_sec_filings.sql
│       ├── intermediate/int_forensic_metrics.sql
│       └── marts/                    # Core Analytical SQL Models
│           ├── fct_anomaly_detection.sql
│           ├── fct_narrative_drift.sql
│           ├── fct_red_flag_report.sql
│           └── rpt_boilerplate_offenders.sql
├── ml_engine/                       
│   └── fraud_model.py                # Isolation Forest Scoring
└── analysis/                        
    ├── density_visualizer.py         # Seaborn JointPlots
    ├── forensic_triangulation.py     # SEC vs Market Regressions
    ├── executive_visuals.py          # Radar Charts & Time-Series
    └── forensic_alerter.py           # Gemini Automated Emailing
```

---

## 🚀 Setup & Execution Instructions

### 1. Prerequisites
Ensure you have Python 3.10+ installed. You will also need a Google Cloud Service Account JSON key (`gcp-service-account.json`) and a populated `.env` file in the root directory containing your API keys and database URIs.

### 2. Installation
Clone the repository and install the required dependencies:
```bash
pip install -r requirements.txt
```
*(Ensure you have also downloaded the TextBlob corpora by running: `python -m textblob.download_corpora`)*

### 3. Launching the Platform
The entire pipeline is orchestrated via Dagster. To launch the Web UI and trigger the audit:
```bash
dagster dev -f orchestrate/assets.py
```
Navigate to `http://localhost:3000` in your browser and click **"Materialize All"**.

---

## 📊 Outputs
Upon a successful run, the platform will generate a suite of executive-ready visualizations in the `analysis/plots/` directory and dispatch a Gen-AI summary email to the designated audit team.
```

***

This covers everything from the overarching business logic to the exact terminal commands needed to run the code. 

You and Shilpa have built something exceptional here. Is there anything else you need before the big presentation, perhaps a quick test of the Gemini email prompt to make sure it looks perfect?