# 🎵 Music Tempo Cognitive Test

This project is a **Flask-based web application** designed to study the effect of music tempo on cognitive performance.  
Participants complete a series of steps including consent, a demographic questionnaire, the ARCES attentional control scale, and three experimental tasks under different music conditions. Their responses and trial data are automatically saved in Excel files for later analysis.  

---

## 🚀 Features

- Intro and consent workflow  
- Demographic & background questionnaire  
- **ARCES scale** (12 questions) for attentional control  
- Three experimental conditions:  
  - 🐢 Slow tempo music  
  - 🚫 No music  
  - ⚡ Fast tempo music  
- Task order is randomized for each participant  
- Trial-by-trial logging of:  
  - Stimulus  
  - Congruency  
  - Expected response key  
  - Accuracy (correct/incorrect)  
  - Response time (ms)  
- Automatic Excel export to `/data/responsesX.xlsx`  

---

## 🛠 Tech Stack

- [Flask](https://flask.palletsprojects.com/) — backend framework  
- [openpyxl](https://openpyxl.readthedocs.io/) — Excel file handling  
- HTML/CSS/JavaScript — front-end interaction and task design  
- Python standard library (`os`, `datetime`, `random`, `session`)  

---

## 📂 Project Structure

```plaintext
.
├── templates/            # HTML templates (Intro.html, consent.html, etc.)
├── static/               # CSS/JS files for tasks and styling
├── data/                 # Folder where Excel results are saved
├── app.py                # Main Flask application
├── requirements.txt      # Dependencies (Flask, openpyxl)
└── README.md             # Project documentation
