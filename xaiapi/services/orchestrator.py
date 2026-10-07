import pandas as pd
import numpy as np
import shap
from sklearn.inspection import permutation_importance

class Orchestrator:
    def __init__(self, df: pd.DataFrame, model, sample_index: int):
        self.df = df
        self.model = model
        self.sample_index = sample_index
        # Drop target if it exists, otherwise use all columns
        self.X = df.drop(columns=[col for col in df.columns if col.lower() == 'target'], errors='ignore')
        self.sample = self.X.iloc[sample_index]
    
    def explain_shap(self):
        """SHAP force plot + dependence."""
        try:
            explainer = shap.TreeExplainer(self.model)
            shap_values = explainer.shap_values(self.X)
            
            # For binary classification, take class 1
            if isinstance(shap_values, list):
                shap_values = shap_values[1]
            
            sample_shap = np.asarray(shap_values[self.sample_index]).flatten()
            base_value = explainer.expected_value
            if isinstance(base_value, list):
                base_value = base_value[1]
            
            # Safe conversion to float
            base_value = float(base_value) if np.isscalar(base_value) else float(np.asarray(base_value).flat[0])
            
            # Prediction
            pred_proba = self.model.predict_proba([self.sample])[0]
            model_output = float(pred_proba[1]) if len(pred_proba) > 1 else float(pred_proba[0])
            
            # Force plot data
            force_data = {
                "base_value": base_value,
                "model_output": model_output,
                "features": [
                    {
                        "name": str(col),
                        "value": float(self.sample[col]),
                        "shap_value": float(sample_shap[i]),
                    }
                    for i, col in enumerate(self.X.columns)
                ],
            }
            
            # Sort by absolute SHAP value
            force_data["features"].sort(key=lambda x: abs(x["shap_value"]), reverse=True)
            
            return {
                "technique": "shap",
                "sample_index": self.sample_index,
                "force_plot_data": force_data,
                "top_features": force_data["features"][:10],
            }
        except Exception as e:
            import traceback
            return {"error": str(e), "traceback": traceback.format_exc(), "technique": "shap"}
        
    def explain_lime(self):
        """LIME local explanation."""
        try:
            from lime import lime_tabular  # Import the module, not the class
            
            explainer = lime_tabular.LimeTabularExplainer(  # Use module.Class
                self.X.values,
                feature_names=self.X.columns.tolist(),
                class_names=["no_survive", "survive"],
                mode="classification"
            )
            
            exp = explainer.explain_instance(
                self.sample.values,
                self.model.predict_proba,
                num_features=10
            )
            
            feature_weights = exp.as_list()
            
            return {
                "technique": "lime",
                "sample_index": self.sample_index,
                "prediction": float(self.model.predict_proba([self.sample])[0][1]),
                "explanation": [(f, float(w)) for f, w in feature_weights],
            }
        except Exception as e:
            return {"error": str(e), "technique": "lime"}
    
    def explain_importance(self):
        """Permutation importance - works with available features."""
        try:
            from sklearn.inspection import permutation_importance
            
            # Get features that model was trained with
            model_features = set(self.model.feature_names_in_)
            available_features = set(self.X.columns)
            
            # Use only features that exist in both
            common_features = list(model_features & available_features)
            
            if not common_features:
                return {
                    "error": f"No common features. Model trained on: {list(model_features)}, Data has: {list(available_features)}",
                    "technique": "importance"
                }
            
            X_subset = self.X[common_features]
            
            # Use model predictions as target (since we don't have ground truth)
            y = self.model.predict(X_subset)
            
            result = permutation_importance(
                self.model,
                X_subset,
                y,
                n_repeats=10,
                random_state=42,
            )
            
            importance_dict = {
                str(col): float(importance)
                for col, importance in zip(X_subset.columns, result.importances_mean)
            }
            
            sorted_importance = dict(sorted(
                importance_dict.items(),
                key=lambda x: abs(x[1]),
                reverse=True
            ))
            
            return {
                "technique": "importance",
                "sample_index": self.sample_index,
                "importances": sorted_importance,
                "top_features": list(sorted_importance.items())[:10],
                "note": f"Calculated on {len(common_features)} common features"
            }
        except Exception as e:
            return {"error": str(e), "technique": "importance"}
    
    def explain_saliency(self):
        """Gradient-based saliency approximation."""
        try:
            saliency_scores = {}
            baseline_pred = self.model.predict_proba([self.sample])[0][1]
            
            for i, col in enumerate(self.X.columns):
                sample_perturbed = self.sample.copy()
                sample_perturbed[col] = self.X[col].mean()
                
                perturbed_pred = self.model.predict_proba([sample_perturbed])[0][1]
                saliency = abs(baseline_pred - perturbed_pred)
                saliency_scores[str(col)] = float(saliency)
            
            return {
                "technique": "saliency",
                "sample_index": self.sample_index,
                "saliency_scores": saliency_scores,
                "top_features": sorted(
                    saliency_scores.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10],
            }
        except Exception as e:
            return {"error": str(e), "technique": "saliency"}