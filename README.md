# Smart Core Hospital Intelligence

A lightweight healthcare operations analytics application for hospital occupancy, crowding, service availability, and data quality reporting.

## Features
- FastAPI backend with SQLite persistence
- Streamlit dashboard in Arabic-first layout
- CSV/XLSX import preview and validation
- Data quality checks and duplicate detection
- Occupancy, crowding, and service analytics
- Explainable AI-style insights without fabricated facts
- Forecasting only when enough historical data exists
- Synthetic sample dataset for demo

## Project structure
- app/ — backend application and services
- dashboard/ — Streamlit dashboard
- data/samples/ — synthetic sample files
- tests/ — automated pytest tests

## Quick start (Windows)
1. Create and activate a virtual environment:
   python -m venv .venv
   .venv\Scripts\activate
2. Install dependencies:
   pip install -r requirements.txt
3. Run the app:
   run_app.bat
4. Open the browser to:
   - API: http://localhost:8000/docs
   - Dashboard: http://localhost:8501

## Environment variables
Copy `.env.example` to `.env` and adjust values as needed.

## Notes
This is an MVP for local development and demonstration. It is not a substitute for official hospital data integration or regulated healthcare compliance.
