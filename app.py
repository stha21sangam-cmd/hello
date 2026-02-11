from flask import Flask, render_template, request, redirect
import requests
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

API_KEY = "83kCAri6RbaIRdqGBe1RLYClnZZ1h44TFEa9RnhpLC232bFeR9"   # Replace this

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    if "image" not in request.files:
        return redirect("/")

    file = request.files["image"]
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    with open(filepath, "rb") as img:
        response = requests.post(
            "https://api.plant.id/v2/health_assessment",
            headers={"Api-Key": API_KEY},
            files={"images": img},
            data={"organs": "leaf"}
        )

    result = response.json()

    try:
        disease = result["health_assessment"]["diseases"][0]["name"]
        probability = round(result["health_assessment"]["diseases"][0]["probability"] * 100, 2)
        severity = "High" if probability > 70 else "Medium" if probability > 40 else "Low"
    except:
        disease = "Healthy or Unknown"
        probability = 0
        severity = "None"

    advice = generate_advice(disease)

    return render_template("result.html",
                           image=filename,
                           disease=disease,
                           probability=probability,
                           severity=severity,
                           advice=advice)

def generate_advice(disease):
    if "blight" in disease.lower():
        return "Remove infected leaves. Use pesticide spray. Avoid overhead watering."
    elif "rust" in disease.lower():
        return "Improve air circulation. Apply sulfur-based fungicide."
    else:
        return "Maintain proper watering and monitor regularly."

if __name__ == "__main__":
    app.run(debug=True)