import os
import json
from pathlib import Path

from flask import Flask, render_template, send_from_directory
from dotenv import load_dotenv
import requests
from jinja2 import DictLoader

load_dotenv()

GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "yourusername")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

RESUME_DIR = Path("resume")
RESUME_FILE = "Anant_Sawant_CV.pdf"

HEADERS = {"Accept": "application/vnd.github+json"}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"token {GITHUB_TOKEN}"

app = Flask(__name__)

TEMPLATES = {
"index.html": """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{{ info.name }} - Portfolio</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>

<body class="bg-gray-50 text-gray-900">

<section class="bg-white shadow py-10 px-6 md:px-20">
  <h1 class="text-4xl font-bold">{{ info.name }}</h1>

  <p class="text-gray-600 text-lg mt-2">
    {{ info.location }} • {{ info.email }} • {{ info.phone }}
  </p>

  <h2 class="text-2xl font-semibold mt-6">Summary</h2>
  <p class="mt-2 text-gray-700">
    {{ info.summary }}
  </p>

  <h2 class="text-2xl font-semibold mt-6">Skills</h2>
  <div class="flex flex-wrap gap-2 mt-2">
    {% for s in info.skills %}
      <span class="px-3 py-1 text-sm bg-gray-200 rounded">{{ s }}</span>
    {% endfor %}
  </div>

  <h2 class="text-2xl font-semibold mt-6">Resume</h2>

  {% if resume_exists %}
   
    <a href="/resume/{{ resume_file }}" target="_blank"
       class="inline-block mt-3 px-4 py-2 bg-indigo-600 text-white rounded">
      Open Resume in New Tab
    </a>
  {% else %}
    <p class="text-red-600 mt-3">
      Resume not found. Place it at <b>resume/{{ resume_file }}</b>
    </p>
  {% endif %}
</section>

<section class="px-6 md:px-20 py-12">
  <h2 class="text-3xl font-semibold mb-6">Projects</h2>

  {% if repos %}
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    {% for r in repos %}
      <div class="bg-white p-5 shadow rounded border">
        <h3 class="text-xl font-semibold">
          <a href="{{ r.html_url }}" target="_blank"
             class="text-indigo-600 hover:underline">
            {{ r.name }}
          </a>
        </h3>

        <p class="text-sm text-gray-700 mt-2">
          {{ r.description or "No description provided." }}
        </p>

        <p class="text-xs text-gray-500 mt-2">
          Updated: {{ r.updated_at[:10] }} |
          {{ r.language or "Unknown" }}
        </p>

        {% if r.homepage %}
          <a href="{{ r.homepage }}" target="_blank"
             class="text-xs text-indigo-600 underline mt-2 block">
            Live Demo
          </a>
        {% endif %}
      </div>
    {% endfor %}
  </div>
  {% else %}
    <p class="text-gray-600">No GitHub projects found.</p>
  {% endif %}
</section>

</body>
</html>
"""
}

app.jinja_loader = DictLoader(TEMPLATES)

def github_api(path):
    url = "https://api.github.com" + path
    r = requests.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    return r.json()

def fetch_repos():
    repos = github_api(f"/users/{GITHUB_USERNAME}/repos?per_page=200")
    return [
        {
            "name": r["name"],
            "html_url": r["html_url"],
            "description": r.get("description"),
            "language": r.get("language"),
            "homepage": r.get("homepage"),
            "updated_at": r.get("updated_at", ""),
        }
        for r in repos
    ]

@app.route("/")
def home():
    repos = fetch_repos()

    info = {
        "name": "Anant Sawant",
        "location": "Panjim, Goa",
        "email": "anant292004@gmail.com",
        "phone": "(+91) 8999545732",
        "summary": (
    "Enthusiastic developer with hands-on experience in Python projects "
    "and web application development. Skilled in building real-world "
    "applications using Python and modern web technologies, with a strong "
    "interest in pursuing a career as a Python Developer and continuously "
    "improving problem-solving and system design skills."
),

        "skills": [
            "Python", "HTML", "CSS", "JavaScript", "React.js",
            "Next.js", "Node.js", "Express.js", "MongoDB",
            "SQL", "Tailwind CSS","Django","Flask"
        ],
    }

    return render_template(
        "index.html",
        info=info,
        repos=repos,
        resume_exists=(RESUME_DIR / RESUME_FILE).exists(),
        resume_file=RESUME_FILE
    )

@app.route("/resume/<path:file>")
def resume_file(file):
    return send_from_directory(RESUME_DIR, file)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
