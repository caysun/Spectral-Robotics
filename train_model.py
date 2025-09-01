import json
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib

# Load JSON file
with open("trainingData/calibratedReadings.json", "r") as f:
    data = json.load(f)

# Convert to DataFrame
df = pd.DataFrame(data)
df.head()

# Split features and labels (x/y)
X = df.drop(columns=["label"])   # all columns except label
y = df["label"]                  # target column

# Split data into train/test (80/20)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Create and train Random Forest
rf_model = RandomForestClassifier(
    n_estimators=100,  # number of trees
    max_depth=None,    # grow trees until leaves are pure
    random_state=42
)
rf_model.fit(X_train, y_train)

# Evaluate
y_pred = rf_model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

# Save trained model
joblib.dump(rf_model, "random_forest_model.joblib")