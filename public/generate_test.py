import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib

# Quick test data
np.random.seed(42)
X = np.random.randn(100, 5)
y = (X[:, 0] > 0).astype(int)

df = pd.DataFrame(X, columns=['A', 'B', 'C', 'D', 'E'])
df.to_csv('test_data.csv', index=False)

model = RandomForestClassifier(n_estimators=10, random_state=42)
model.fit(X, y)
joblib.dump(model, 'test_model.pkl')

print("Created test_data.csv and test_model.pkl in public folder")