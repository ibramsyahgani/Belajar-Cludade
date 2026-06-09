import base64
import json
import re
from pathlib import Path
import google.generativeai as genai
from .config import load_config, get_gemini_api_key
from .models import CVData


def extract_json(text: str) -> dict:
    """Extract JSON from AI response, stripping markdown fences if present."""
    text = text.strip()
    # Remove ```json ... ``` or ``` ... ```
    text = re.sub(r'^```(?:json)?\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    return json.loads(text)


async def process_cv_with_gemini(file_bytes: bytes, mime_type: str, user_name: str, user_email: str) -> CVData:
    config = load_config()
    api_key = get_gemini_api_key()

    if not api_key:
        raise ValueError("GEMINI_API_KEY tidak dikonfigurasi. Tambahkan ke file .env.")

    genai.configure(api_key=api_key)

    model_name = config.get("ai_model", "gemini-2.5-flash")
    system_prompt = config.get("reformat_system_prompt", "")

    json_schema = """{
  "bidang": "default|agrikultur|psikologi_hr|logistik|hse_esg",
  "header": { "nama": "", "lokasi": "", "email": "", "telepon": "", "linkedin_atau_portfolio": "" },
  "ringkasan_profesional": "",
  "pendidikan": [
    { "institusi": "", "lokasi": "", "periode": "", "jurusan_gelar": "", "ipk": "", "skripsi": "", "pelatihan": [""] }
  ],
  "pengalaman": [
    { "organisasi": "", "lokasi": "", "periode": "", "posisi": "", "poin": [""] }
  ],
  "sertifikasi_pencapaian": [""],
  "leadership_activities": [
    { "organisasi": "", "lokasi": "", "periode": "", "peran": "", "poin": [""] }
  ],
  "kemampuan": { "hard_skills": [""], "tools_software": [""], "bahasa": [""] },
  "notes": ""
}"""

    full_system = (
        system_prompt
        + f"\n\nNama pemilik CV: {user_name}\nEmail pemilik CV: {user_email}"
        + f"\n\nSkema JSON yang harus dikembalikan:\n{json_schema}"
    )

    model = genai.GenerativeModel(
        model_name=model_name,
        system_instruction=full_system
    )

    file_part = {
        "inline_data": {
            "mime_type": mime_type,
            "data": base64.b64encode(file_bytes).decode("utf-8")
        }
    }

    prompt = (
        "Baca CV ini dan kembalikan data terstruktur sesuai skema JSON yang diberikan. "
        "Pastikan grounded, gunakan placeholder [____] untuk angka yang tidak ada, "
        "dan awali setiap bullet pengalaman dengan action verb."
    )

    response = model.generate_content([file_part, prompt])

    try:
        cv_dict = extract_json(response.text)
        # If header email is empty, use the user-provided email
        if not cv_dict.get("header", {}).get("email") and user_email:
            cv_dict.setdefault("header", {})["email"] = user_email
        if not cv_dict.get("header", {}).get("nama") and user_name:
            cv_dict.setdefault("header", {})["nama"] = user_name
        return CVData(**cv_dict)
    except (json.JSONDecodeError, Exception) as e:
        raise ValueError(f"AI tidak mengembalikan JSON valid: {e}\nResponse: {response.text[:500]}")
