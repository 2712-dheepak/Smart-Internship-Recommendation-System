# Smart Internship Recommendation System

## Overview

The Smart Internship Recommendation System is a Machine Learning-based web application that recommends suitable internship roles for students based on their academic performance, technical skills, projects, certifications, and interests.

The system analyzes candidate information, predicts internship roles, calculates candidate scores, generates reports, and stores candidate records in a database for future analysis.

---

## Features

* Candidate Registration Form
* Internship Recommendation using Machine Learning
* Candidate Score Calculation
* Resume PDF Analysis
* Internship Availability Management
* Candidate Dashboard
* Admin Login Panel
* Candidate Report Generation
* SQLite Database Integration
* Responsive User Interface

---

## Technologies Used

### Frontend

* HTML5
* CSS3
* Bootstrap 5
* JavaScript

### Backend

* Python
* Flask

### Machine Learning

* Scikit-Learn
* Pandas
* NumPy

### Database

* SQLite

### Additional Libraries

* PyPDF2

---

## Project Structure

```
Smart-Internship-Recommendation-System/

├── app.py
├── database.db
├── requirements.txt
├── README.md

├── dataset/
│   ├── candidates.csv
│   └── generate_dataset.py

├── models/
│   ├── model.pkl
│   ├── mlb.pkl
│   ├── label_encoder.pkl
│   └── train_model.py

├── static/
│   └── css/
│       └── style.css

├── templates/
│   ├── home.html
│   ├── index.html
│   ├── result.html
│   ├── dashboard.html
│   ├── admin.html
│   ├── admin_login.html
│   ├── availability.html
│   └── candidate_report.html
```

---

## Machine Learning Workflow

1. Candidate information is collected through the web form.
2. Skills and academic details are processed.
3. Trained ML model predicts the most suitable internship role.
4. Candidate score is calculated.
5. Results are displayed and stored in the database.
6. Dashboard displays all candidate records.

---

## Installation

### Clone Repository

```bash
git clone https://github.com/2712-dheepak/Smart-Internship-Recommendation-System.git
```

### Move to Project Directory

```bash
cd Smart-Internship-Recommendation-System
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Application

```bash
python app.py
```

---

## Deployed Application

Render Deployment:

https://smart-internship-recommendation-system-f77s.onrender.com

---

## GitHub Repository

https://github.com/2712-dheepak/Smart-Internship-Recommendation-System

---

## Future Enhancements

* Resume Ranking System
* Internship Matching using NLP
* Email Notifications
* Student Login System
* Company Portal
* Cloud Database Integration
* Advanced Analytics Dashboard

---

## Author

Dheepak Kumar

Electronics and Communication Engineering (ECE)

Machine Learning & Software Development Enthusiast

---

## License

This project is developed for educational and internship purposes.
