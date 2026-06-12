import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, MultiLabelBinarizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pickle
import os

df = pd.read_csv("dataset/candidates.csv")

all_skills = [
    "Python", "Machine Learning", "TensorFlow", "Pandas", "NumPy",
    "Statistics", "SQL", "Data Visualization",
    "JavaScript", "React", "Node.js", "HTML", "CSS", "MongoDB",
    "Flutter", "Dart", "Firebase", "Mobile Development",
    "Figma", "Adobe XD", "Wireframing", "Prototyping", "User Research",
    "Linux", "Docker", "CI/CD", "Jenkins", "Bash",
    "AWS", "Azure", "GCP", "Terraform", "Cloud Architecture",
    "Communication", "MS Office", "Recruitment", "HR Policies", "Excel"
]

mlb = MultiLabelBinarizer(classes=all_skills)
skills_list = df["skills"].apply(lambda x: [s.strip() for s in x.split(",")])
skills_encoded = mlb.fit_transform(skills_list)

X_skills = pd.DataFrame(skills_encoded, columns=mlb.classes_)
X_num = df[["cgpa", "projects", "certifications", "experience_level"]].reset_index(drop=True)
X = pd.concat([X_num, X_skills], axis=1)

le = LabelEncoder()
y = le.fit_transform(df["role"])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

acc = accuracy_score(y_test, model.predict(X_test))
print(f"Model Accuracy: {acc*100:.2f}%")

os.makedirs("models", exist_ok=True)
with open("models/model.pkl", "wb") as f:
    pickle.dump(model, f)
with open("models/label_encoder.pkl", "wb") as f:
    pickle.dump(le, f)
with open("models/mlb.pkl", "wb") as f:
    pickle.dump(mlb, f)

print("Model saved to models/")