import os
import requests
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

app = Flask(__name__)

# =============================
# CONFIG
# =============================
API_KEY = "2b10Z95xm4xGPxuHmI38kZrJ"
PLANT_NET_URL = f"https://my-api.plantnet.org/v2/identify/all?api-key={API_KEY}"

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}

# =============================
# Helper
# =============================
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# =============================
# Routes
# =============================
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":

        if "plant_image" not in request.files:
            return "No file uploaded"

        file = request.files["plant_image"]

        if file.filename == "":
            return "No file selected"

        if file and allowed_file(file.filename):

            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)

            # Send to PlantNet API (multipart/form-data)
            with open(filepath, "rb") as img:
                files = {
                    "images": (filename, img, "image/jpeg")
                }
                data = {
                    "organs": "leaf"
                }

                response = requests.post(
                    PLANT_NET_URL,
                    files=files,
                    data=data
                )

            if response.status_code != 200:
                return f"API Error: {response.text}"

            result = response.json()

            if "results" not in result or len(result["results"]) == 0:
                return "No plant detected."

            best_match = result["results"][0]

            plant_name = best_match["species"]["scientificNameWithoutAuthor"]
            common_names = best_match["species"].get("commonNames", [])
            confidence = round(best_match["score"] * 100, 2)

            # ====== Simulated Health AI Layer ======
            if confidence > 80:
                health_status = "Plant appears Healthy 🌿"
                needs = "Regular watering and full sunlight."
            elif confidence > 50:
                health_status = "Plant condition moderate ⚠️"
                needs = "Check soil moisture and sunlight exposure."
            else:
                health_status = "Plant may be stressed 🚨"
                needs = "Inspect for pests, diseases, or nutrient deficiency."

            return render_template(
                "result.html",
                image=filepath,
                plant_name=plant_name,
                common_names=common_names,
                confidence=confidence,
                health_status=health_status,
                needs=needs
            )

        else:
            return "Invalid file type. Only JPG, JPEG, PNG allowed."

    return render_template("home.html")


if __name__ == "__main__":
    app.run(debug=True)
