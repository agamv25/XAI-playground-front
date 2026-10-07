import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib

# Load the Titanic CSV
df = pd.read_csv('Titanic-Dataset.csv')

print(f"Original shape: {df.shape}")

# Drop rows with missing target
df = df.dropna(subset=['Survived'])

# Handle missing values
df['Age'].fillna(df['Age'].median(), inplace=True)
df['Embarked'].fillna(df['Embarked'].mode()[0], inplace=True)

# Drop non-useful columns
df = df.drop(columns=['PassengerId', 'Name', 'Ticket', 'Cabin'])

# Encode categorical columns
le_sex = LabelEncoder()
le_embarked = LabelEncoder()

df['Sex'] = le_sex.fit_transform(df['Sex'])
df['Embarked'] = le_embarked.fit_transform(df['Embarked'])

# Separate target and features
target = df['Survived']
X = df.drop(columns=['Survived'])

print(f"Final shape: {X.shape}")
print(f"Features: {X.columns.tolist()}")

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=15)
model.fit(X, target)

# Save model
joblib.dump(model, 'titanic_model.pkl')
accuracy = model.score(X, target)
print(f"\n✓ Saved titanic_model.pkl")
print(f"✓ Model accuracy: {accuracy:.2f}")

# Save clean CSV (without target)
X.to_csv('titanic_data.csv', index=False)
print(f"✓ Saved titanic_data.csv ({X.shape[0]} rows, {X.shape[1]} features)")