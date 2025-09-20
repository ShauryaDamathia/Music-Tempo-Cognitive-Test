from flask import Flask, request, render_template, redirect, session, url_for, jsonify
import os
import openpyxl
from datetime import datetime
from random import shuffle

app = Flask(__name__)
app.secret_key = "your_secret_key"
UPLOAD_FOLDER = "data"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def intro():
    return render_template("Intro.html")

@app.route('/consent')
def consent():
    return render_template("consent.html")

@app.route('/questionaire')
def questionaire():
    return render_template("questionaire.html")

@app.route('/arces', methods=["GET", "POST"])
def arces():
    if request.method == "POST":
        form_data = request.form.to_dict()
        session['responses'] = session.get('responses', {})
        session['responses']['arces'] = form_data
        session.modified = True

        score = 0
        for i in range(1, 13):
            try:
                score += int(form_data.get(f'q{i}', 0))
            except (ValueError, TypeError):
                continue

        if score < 30:
            return redirect(url_for('thankyou'))
        else:
            return redirect(url_for('index'))

    return render_template("arces.html")

@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/practice')
def practice():
    return render_template("practice.html")

@app.route('/task')
def task():
    return render_template("task.html")

@app.route('/first')
def first():
    return render_template("first.html") 

@app.route('/slowtask')
def slowtask():
    return render_template("slowtask.html")

@app.route('/second')
def second(): 
    return render_template("second.html") 

@app.route('/notask')
def notask():
    return render_template("notask.html")

@app.route('/third')
def third():
    if 'task_order' not in session or session.get('task_index', 0) != 2:
        return redirect(url_for('first'))  
    return render_template("third.html")

@app.route('/fasttask')
def fasttask():
    return render_template("fasttask.html")

@app.route('/Alldone')
def alldone():
    return render_template("Alldone.html")

@app.route('/thankyou')
def thankyou():
    return render_template("45Thankyou.html")

@app.route('/save_data', methods=['POST'])
def save_data():
    page = request.form.get("page")
    data = request.form.to_dict(flat=False)
    cleaned_data = {}

    if page == "questionaire":
        for key, value in data.items():
            if key not in ["music-genre[]", "other-genre"]:
                cleaned_data[key] = value[0]

        genres = []
        if "music-genre[]" in data:
            genres.extend(data["music-genre[]"])
        if "other-genre" in data and data["other-genre"][0]:
            genres.append(data["other-genre"][0])
        cleaned_data["music_genre"] = ", ".join(genres)
    else:
        for key, value in data.items():
            cleaned_data[key] = value[0] if isinstance(value, list) and len(value) == 1 else value

    responses = session.get("responses", {})
    responses[page] = cleaned_data
    session["responses"] = responses

    if page == "consent":
        return redirect("/questionaire")
    elif page == "questionaire":
        return redirect("/arces")
    elif page == "arces":
        score = 0
        for i in range(1, 13):
            try:
                score += int(cleaned_data.get(f"q{i}", 0))
            except ValueError:
                continue
        return redirect("/thankyou") if score < 30 else redirect("/index")
    elif page in ["slowtask", "notask", "fasttask"]:
        return redirect(f"/{page}")

@app.route('/begin_task')
def begin_task():
    task_index = session.get('task_index', 0)
    task_order = session.get('task_order', [])
    
    if task_index >= len(task_order):
        return redirect(url_for('alldone'))
   
    current_task = task_order[task_index]
    return redirect(url_for(current_task))

@app.route('/next_task')
def next_task():
    task_order = session.get("task_order", [])
    task_index = session.get("task_index", 0) + 1
    
    if task_index >= len(task_order):
        return redirect(url_for('alldone'))
    
    session["task_index"] = task_index
    
    if task_index == 1:
        return redirect(url_for('second'))
    elif task_index == 2:
        return redirect(url_for('third'))
    else:
        return redirect(url_for('alldone'))
    
@app.route('/save_flanker_data', methods=['POST'])
def save_flanker_data():
    data = request.get_json()
    trials = data.get('trials', [])
    task_type = data.get('task_type')

    if not task_type or task_type not in ['slowtask', 'notask', 'fasttask']:
        return jsonify({"error": "Invalid task type."}), 400

    # Save the trials in session for the given task
    session[f"{task_type}_trials"] = trials
    session.modified = True

    # If it's the last task (fasttask), save everything to Excel
    if task_type == 'fasttask':
        responses = session.get("responses", {})
        if not responses:
            return jsonify({"error": "No session data found."}), 400

        filename = get_next_filename(UPLOAD_FOLDER)
        workbook = openpyxl.Workbook()
        sheet = workbook.active

        # Write Consent Section
        sheet.append(["Consent Section"])
        consent_data = responses.get("consent", {})
        sheet.append(list(consent_data.keys()))
        sheet.append(list(consent_data.values()))

        # Write Questionnaire Section
        sheet.append([])
        sheet.append(["Questionnaire Section"])
        questionaire_data = responses.get("questionaire", {})
        sheet.append(list(questionaire_data.keys()))
        sheet.append(list(questionaire_data.values()))

        # Write ARCES Section
        sheet.append([])
        sheet.append(["ARCES Section"])
        arces_data = responses.get("arces", {})
        sheet.append([f"q{i}" for i in range(1, 13)])
        sheet.append([arces_data.get(f"q{i}", "") for i in range(1, 13)])
        score = sum(int(arces_data.get(f"q{i}", 0)) for i in range(1, 13))
        sheet.append([])
        sheet.append(["Total ARCES Score", score])

        # Add function to write trials
        def write_trials(section_title, task_key):
            sheet.append([])
            sheet.append([section_title])
            trials_data = session.get(task_key, [])
            headers = ["Trial Number", "Stimulus", "Congruency", "Expected Key", "Correct", "Response Time (ms)"]
            sheet.append(headers)
            for trial in trials_data:
                row = [
                    trial.get("trial_number"),
                    trial.get("stimulus"),
                    trial.get("congruency"),
                    trial.get("expected_key"),
                    trial.get("correct"),
                    trial.get("response_time_ms"),
                ]
                sheet.append(row)

        # Write all trial sections
        write_trials("First Music Task Section", "slowtask_trials")
        write_trials("Second Task Section", "notask_trials")
        write_trials("Third Music Task Section", "fasttask_trials")

        workbook.save(filename)

        return jsonify({"message": "All data saved successfully."}), 200

    return jsonify({"message": f"{task_type} data saved temporarily."}), 200

def get_next_filename(base_folder):
    i = 1
    while True:
        filename = os.path.join(base_folder, f"responses{i}.xlsx")
        if not os.path.exists(filename):
            return filename  
        i += 1  

if __name__ == '__main__':
    app.run(debug=True)