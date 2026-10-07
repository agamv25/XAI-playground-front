from fastapi import FastAPI, UploadFile, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
import uuid
import json
from pathlib import Path
import pandas as pd
import joblib

app = FastAPI()

# CORS for localhost dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STORAGE_DIR = Path("./analyses")
STORAGE_DIR.mkdir(exist_ok=True)

@app.post("/api/analyses")
async def create_analysis(csv_file: UploadFile, model_file: UploadFile):
    """Upload CSV + model, validate, return dataset stats."""
    analysis_id = str(uuid.uuid4())
    analysis_dir = STORAGE_DIR / analysis_id
    analysis_dir.mkdir()
    
    # Save files
    csv_path = analysis_dir / "data.csv"
    model_path = analysis_dir / "model.pkl"
    
    with open(csv_path, "wb") as f:
        f.write(await csv_file.read())
    with open(model_path, "wb") as f:
        f.write(await model_file.read())
    
    # Load & validate
        # Load & validate
        # Load & validate
    from services.upload import load_data, load_model
    df = load_data(csv_path)
    model = load_model(model_path)
    
    # Save cleaned CSV
    df.to_csv(csv_path, index=False)
    
    # Compute dataset stats
    stats = {
        "rows": len(df),
        "features": len(df.columns),
        "missing": 0,  # Already filled
        "data_types": df.dtypes.astype(str).to_dict(),
    }
    
    # Store metadata
    metadata = {
        "analysis_id": analysis_id,
        "dataset_stats": stats,
        "model_type": type(model).__name__,
    }
    
    with open(analysis_dir / "metadata.json", "w") as f:
        json.dump(metadata, f)
    
    return {
        "analysis_id": analysis_id,
        "dataset_stats": stats,
        "model_type": type(model).__name__,
    }

@app.post("/api/analyses/{analysis_id}/compute")
async def compute_explanations(
    analysis_id: str,
    techniques: list[str] = Query(...),
    sample_index: int = Query(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Queue computation, return immediately with status."""
    analysis_dir = STORAGE_DIR / analysis_id
    
    # Start async job
    background_tasks.add_task(
        orchestrate_computation,
        analysis_id,
        techniques,
        sample_index
    )
    
    return {
        "analysis_id": analysis_id,
        "status": "computing",
        "sample_index": sample_index,
        "techniques": techniques,
    }

async def orchestrate_computation(analysis_id: str, techniques: list[str], sample_index: int):
    """Run all selected techniques, save results."""
    from services.orchestrator import Orchestrator
    
    analysis_dir = STORAGE_DIR / analysis_id
    
    # Load data & model
    df = pd.read_csv(analysis_dir / "data.csv")
    model = joblib.load(analysis_dir / "model.pkl")
    
    # Run explainers
    orchestrator = Orchestrator(df, model, sample_index)
    results = {}
    
    if "shap" in techniques:
        results["shap"] = orchestrator.explain_shap()
    if "lime" in techniques:
        results["lime"] = orchestrator.explain_lime()
    if "importance" in techniques:
        results["importance"] = orchestrator.explain_importance()
    if "saliency" in techniques:
        results["saliency"] = orchestrator.explain_saliency()
    
    # Save results
    with open(analysis_dir / "results.json", "w") as f:
        json.dump(results, f, default=str)

@app.get("/api/analyses/{analysis_id}/results/{technique}")
async def get_results(analysis_id: str, technique: str):
    """Return cached results for a technique."""
    analysis_dir = STORAGE_DIR / analysis_id
    results_file = analysis_dir / "results.json"
    
    if not results_file.exists():
        return {"status": "computing"}
    
    with open(results_file) as f:
        all_results = json.load(f)
    
    return all_results.get(technique, {})