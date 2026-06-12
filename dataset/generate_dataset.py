import pandas as pd
import numpy as np
import os

np.random.seed(42)

roles = [
    "AI/ML Engineer Intern",
    "Data Science Intern",
    "Full Stack Developer Intern",
    "Flutter Developer Intern",
    "UI/UX Design Intern",
    "DevOps Intern",
    "Cloud Computing Intern",
    "HR Operations Intern"
]

skill_map = {
    "AI/ML Engineer Intern":       ["Python", "Machine Learning", "TensorFlow", "Pandas", "NumPy"],
    "Data Science Intern":         ["Python", "Pandas", "Statistics", "SQL", "Data Visualization"],
    "Full Stack Developer Intern":  ["JavaScript", "React", "Node.js", "HTML", "CSS", "MongoDB"],
    "Flutter Developer Intern":     ["Flutter", "Dart", "Firebase", "Mobile Development"],
    "UI/UX Design Intern":         ["Figma", "Adobe XD", "Wireframing", "Prototyping", "User Research"],
    "DevOps Intern":               ["Linux", "Docker", "CI/CD", "Jenkins", "Bash"],
    "Cloud Computing Intern":      ["AWS", "Azure", "GCP", "Terraform", "Cloud Architecture"],
    "HR Operations Intern":        ["Communication", "MS Office", "Recruitment", "HR Policies", "Excel"]
}

all_skills = list(set(s for skills in skill_map.values() for s in skills))

records = []
for _ in range(400):
    role = np.random.choice(roles)
    primary = skill_map[role]
    candidate_skills = list(np.random.choice(primary, size=min(3, len(primary)), replace=False))
    extra = [s for s in all_skills if s not in primary]
    candidate_skills += list(np.random.choice(extra, size=2, replace=False))

    records.append({
        "cgpa": round(np.random.uniform(5.5, 10.0), 2),
        "projects": np.random.randint(0, 6),
        "certifications": np.random.randint(0, 4),
        "experience_level": np.random.randint(0, 3),
        "skills": ", ".join(candidate_skills),
        "role": role
    })

df = pd.DataFrame(records)
os.makedirs("dataset", exist_ok=True)
df.to_csv("dataset/candidates.csv", index=False)
print(f"Dataset created: {len(df)} rows")