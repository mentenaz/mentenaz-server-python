import os
import time
from datetime import datetime, timezone

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from groq import Groq
from supabase import Client, create_client

load_dotenv()

app = Flask(__name__)
CORS(app, origins=os.getenv("ALLOWED_ORIGIN", "*"))

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# Simple in-memory cache
_cache = {"prompt": None, "timestamp": 0}
CACHE_TTL = 300


def fetch_profile() -> str:
    row = supabase.table("profile").select("*").single().execute().data
    return f"""
== PROFILE ==
Name: {row["full_name"]}
Title: {row["title"]}
Specialization: {row["specialization"]}
Summary: {row["summary"]}
Location: {row["location"]}
Nationality: {row["nationality"]}
Languages: {", ".join(row["languages"])}
Availability: {row["availability_status"]}
Visa Status: {row["visa_status"]}
Dependants: {row["dependants"]}
Notice Period: {row["notice_period"]}
Work Preference: {row["work_preference"]}
Salary Expectation: {row["salary_expectation"]}
Target Countries: {", ".join(row["target_countries"])}
Elevator Pitch: {row["elevator_pitch"]}
Email: {row["email"]}
LinkedIn: {row["linkedin_url"]}
GitHub: {row["github_url"]}
Portfolio: {row["portfolio_url"]}
"""


def fetch_experience() -> str:
    rows = (
        supabase.table("experience").select("*").order("display_order").execute().data
    )
    output = "\n== EXPERIENCE ==\n"
    for r in rows:
        end = "Present" if r["is_current"] else r["end_date"]
        output += f"\n{r['company']} — {r['role']} ({r['start_date']} to {end})\n"
        output += f"{r['description']}\n"
        output += "Responsibilities:\n"
        for resp in r["responsibilities"]:
            output += f"  - {resp}\n"
    return output


def fetch_skills() -> str:
    rows = (
        supabase.table("skills")
        .select("*")
        .order("category")
        .order("display_order")
        .execute()
        .data
    )
    output = "\n== SKILLS ==\n"
    category = None
    for r in rows:
        if r["category"] != category:
            category = r["category"]
            output += f"\n{category}:\n"
        output += f"  - {r['name']} ({r['duration']})\n"
    return output


def fetch_projects() -> str:
    rows = supabase.table("projects").select("*").order("display_order").execute().data
    output = "\n== PROJECTS ==\n"
    for r in rows:
        output += f"\n{r['title']} [{r['status']}]\n"
        output += f"Tech Stack: {', '.join(r['tech_stack'])}\n"
        output += f"Description: {r['description']}\n"
        if r["achievements"]:
            technical = r["achievements"].get("technical", [])
            business = r["achievements"].get("business", [])
            if technical:
                output += "Technical Achievements:\n"
                for a in technical:
                    output += f"  - {a}\n"
            if business:
                output += "Business Achievements:\n"
                for a in business:
                    output += f"  - {a}\n"
    return output


def fetch_skills_progression() -> str:
    rows = (
        supabase.table("skills_progression")
        .select("*")
        .order("display_order")
        .execute()
        .data
    )
    output = "\n== SKILLS PROGRESSION ==\n"
    for r in rows:
        end = "Present" if r["is_current"] else r["period_end"]
        output += f"\n{r['phase_name']} ({r['period_start']} to {end}):\n"
        for skill in r["skills"]:
            output += f"  - {skill}\n"
    return output


def fetch_education() -> str:
    rows = supabase.table("education").select("*").order("display_order").execute().data
    output = "\n== EDUCATION & CERTIFICATIONS ==\n"
    for r in rows:
        status = "In Progress" if r["is_current"] else "Completed"
        output += f"\n{r['institution']} — {r['qualification']}\n"
        output += f"Field: {r['field_of_study']} | Status: {status}\n"
        if r["notes"]:
            output += f"Notes: {r['notes']}\n"
    return output


def build_system_prompt() -> str:
    now = time.time()

    if _cache["prompt"] and (now - _cache["timestamp"]) < CACHE_TTL:
        return _cache["prompt"]

    current_date = datetime.now(timezone.utc).strftime("%B %d, %Y")

    context = (
        fetch_profile()
        + fetch_experience()
        + fetch_skills()
        + fetch_projects()
        + fetch_skills_progression()
        + fetch_education()
    )

    prompt = f"""You are a professional assistant on Francois Huyzers's portfolio website.
    Your job is to answer questions about Francois accurately, concisely, and professionally.
    Use only the information provided below — do not invent or assume anything not listed.
    If asked something unrelated to Francois, politely redirect the conversation.
    If asked for contact details, provide his email and LinkedIn URL.
    Present all education and certification entries exactly as listed without adding commentary, classifications, or comparisons. Do not volunteer opinions about the level or value of any qualification unless directly asked.
    Today's date is {current_date}. Use this when calculating durations or time-based questions. Calculate carefully — for example, November 2024 to April 2026 is 1 year and 5 months, not 5 months.

    {context}
    """

    _cache["prompt"] = prompt
    _cache["timestamp"] = now

    # Temporary debug — remove after confirming education appears

    return prompt


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({"error": "No message provided"}), 400

    try:
        system_prompt = build_system_prompt()
        history = data.get("history", [])

        messages = [{"role": "system", "content": system_prompt}]

        for entry in history:
            messages.append({"role": entry["role"], "content": entry["content"]})

        messages.append({"role": "user", "content": data["message"]})

        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            max_tokens=500,
        )

        return jsonify({"reply": response.choices[0].message.content})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
