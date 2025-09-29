#!/usr/bin/env python3
"""
Register multiple Juice Shop users from a CSV and verify by logging in.

CSV columns (header required):
- email (required)
- password (required)
- security_question_id (optional, int)
- security_question_text (optional, text; used if ID missing)
- security_answer (required if your instance enforces it)

Outputs: accounts_results.csv with registration and login results.
"""

import csv
import sys
import time
import requests
from pathlib import Path

BASE_URL = "http://localhost:3000"  # change if needed
INPUT_CSV = "accounts.csv"
OUTPUT_CSV = "accounts_results.csv"
TIMEOUT = 15

# ---------- Helpers ----------

def fetch_security_questions():
    """Return a list of questions as [{'id': 1, 'question': '...'}, ...]."""
    url = f"{BASE_URL}/api/SecurityQuestions/"
    r = requests.get(url, timeout=TIMEOUT)
    r.raise_for_status()
    data = r.json()
    # Some builds return {"data":[...]} shape; normalize
    if isinstance(data, dict) and "data" in data:
        return data["data"]
    return data

def resolve_question_id(row, questions):
    """
    Resolve security_question_id from CSV row.
    Prefer explicit ID; fallback to text match (case-insensitive, trimmed).
    Return int or None.
    """
    # 1) Try explicit ID
    qid = (row.get("security_question_id") or "").strip()
    if qid:
        try:
            return int(qid)
        except ValueError:
            pass

    # 2) Try text lookup
    qtxt = (row.get("security_question_text") or "").strip()
    if not qtxt:
        return None

    qtxt_low = qtxt.lower()
    for q in questions:
        if str(q.get("question", "")).strip().lower() == qtxt_low:
            return int(q.get("id"))
    return None

def register_user(email, password, qid, answer):
    """
    POST /api/Users/ -> create user.
    Returns (status_code, json_or_text)
    """
    url = f"{BASE_URL}/api/Users/"
    # Build payload. Juice Shop typically expects this structure:
    payload = {
        "email": email,
        "password": password,
        "passwordRepeat": password
    }
    # Security question (optional on some instances, required on others)
    if qid is not None and answer:
        payload["securityQuestion"] = {"id": qid}
        payload["securityAnswer"] = answer

    r = requests.post(url, json=payload, timeout=TIMEOUT)
    try:
        body = r.json()
    except Exception:
        body = r.text
    return r.status_code, body

def login_user(email, password):
    """
    POST /rest/user/login -> returns token on success.
    Returns (status_code, token_or_message, full_json)
    """
    url = f"{BASE_URL}/rest/user/login"
    payload = {"email": email, "password": password}
    r = requests.post(url, json=payload, timeout=TIMEOUT)
    try:
        data = r.json()
    except Exception:
        return r.status_code, r.text, None

    token = data.get("authentication", {}).get("token") or data.get("token")
    if token:
        return r.status_code, token, data
    # Some versions return directly { "authentication": {...} }
    return r.status_code, data.get("message") or str(data), data

# ---------- Main ----------

def main():
    in_path = Path(INPUT_CSV)
    if not in_path.exists():
        print(f"Input CSV not found: {in_path.resolve()}")
        sys.exit(1)

    # Preload security questions (best-effort; if it fails we still try to register without)
    questions = []
    try:
        questions = fetch_security_questions()
    except Exception as e:
        print(f"Warning: could not fetch security questions ({e}). "
              "If your instance requires them, include 'security_question_id' in CSV.")

    results = []

    with in_path.open(newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"email", "password"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            print(f"CSV missing required columns: {', '.join(missing)}")
            sys.exit(1)

        for row in reader:
            email = (row.get("email") or "").strip()
            password = (row.get("password") or "").strip()
            answer = (row.get("security_answer") or "").strip()

            if not email or not password:
                results.append({
                    "email": email,
                    "registration_status": "skipped",
                    "registration_code": "",
                    "registration_message": "Missing email or password",
                    "login_code": "",
                    "login_result": "",
                    "token": ""
                })
                continue

            qid = resolve_question_id(row, questions) if questions else None

            # Register
            try:
                code, body = register_user(email, password, qid, answer)
            except Exception as e:
                results.append({
                    "email": email,
                    "registration_status": "error",
                    "registration_code": "",
                    "registration_message": f"Request error: {e}",
                    "login_code": "",
                    "login_result": "",
                    "token": ""
                })
                continue

            # Interpret registration result
            reg_status = "created" if code in (200, 201) else "failed"
            reg_msg = ""
            if isinstance(body, dict):
                reg_msg = body.get("status") or body.get("message") or str(body)
            else:
                reg_msg = str(body)

            # Some instances return 200 if user exists, 201 if created; others 401/409 for dupes
            # We'll attempt login regardless, to verify usable credentials.
            time.sleep(0.2)
            l_code, l_msg_or_token, full_json = login_user(email, password)

            token = l_msg_or_token if (l_code == 200 and isinstance(l_msg_or_token, str)) else ""
            login_result = "ok" if l_code == 200 and token else f"error:{l_code}"

            results.append({
                "email": email,
                "registration_status": reg_status,
                "registration_code": code,
                "registration_message": reg_msg,
                "login_code": l_code,
                "login_result": login_result,
                "token": token
            })

    # Write results CSV
    out_path = Path(OUTPUT_CSV)
    with out_path.open("w", newline='', encoding="utf-8") as f:
        fieldnames = [
            "email",
            "registration_status",
            "registration_code",
            "registration_message",
            "login_code",
            "login_result",
            "token"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. Wrote results to {out_path.resolve()}")

if __name__ == "__main__":
    main()
