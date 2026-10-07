import pandas as pd
import joblib
from pathlib import Path

def load_data(csv_path: Path) -> pd.DataFrame:
    """Load CSV and keep only numeric columns."""
    df = pd.read_csv(csv_path)
    
    if df.empty:
        raise ValueError("CSV is empty")
    
    # Keep only numeric columns
    df = df.select_dtypes(include=['number'])
    
    if df.empty:
        raise ValueError("No numeric columns found")
    
    # Fill missing values with column mean
    df = df.fillna(df.mean())
    
    return df

def load_model(model_path: Path):
    """Load scikit-learn model from pickle."""
    model = joblib.load(model_path)
    
    if not hasattr(model, 'predict_proba'):
        raise ValueError("Model must support predict_proba (classification)")
    
    return model