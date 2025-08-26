import json
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# 1. Load JSON file
with open("trainingData/formattedData.json", "r") as f:
    data = json.load(f)

# 2. Convert to DataFrame
df = pd.DataFrame(data)
df.head()
# 3. Split features and labels
X = df.drop(columns=["label"])   # all columns except label
y = df["label"]                  # target column

# 4. Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 5. Create and train Random Forest
rf_model = RandomForestClassifier(
    n_estimators=100,  # number of trees
    max_depth=None,    # grow trees until leaves are pure
    random_state=42
)
rf_model.fit(X_train, y_train)

# 6. Evaluate
y_pred = rf_model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

# 7. Save trained model (optional)
import joblib
joblib.dump(rf_model, "random_forest_model.pkl")