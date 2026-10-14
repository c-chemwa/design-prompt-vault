import os
import json
import urllib.request
import urllib.parse
from datetime import datetime, timezone

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
DATA_FILE = "data.json"

def fetch_live_signals():
    """Pulls live design, frontend, and AI workflow signals from free public JSON APIs."""
    signals = []
    # Source 1: Algolia Hacker News API (Design, UI, Motion, Typography, AI Workflows)
    hn_url = "https://hn.algolia.com/api/v1/search_by_date?query=design+OR+UI+OR+typography+OR+motion+OR+shader+OR+prompt&tags=story&hitsPerPage=8"
    try:
        req = urllib.request.Request(hn_url, headers={"User-Agent": "DesignVaultBot/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            for hit in data.get("hits", []):
                if hit.get("title"):
                    signals.append(hit["title"])
    except Exception as e:
        print(f"HN fetch warning: {e}")

    # Source 2: DEV.to Public API (Design & Frontend tag)
    dev_url = "https://dev.to/api/articles?tag=design&per_page=6"
    try:
        req = urllib.request.Request(dev_url, headers={"User-Agent": "DesignVaultBot/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            articles = json.loads(resp.read().decode("utf-8"))
            for art in articles:
                if art.get("title"):
                    signals.append(f"{art['title']} - {art.get('description', '')}")
    except Exception as e:
        print(f"DEV fetch warning: {e}")

    return signals[:12] if signals else [
        "Kinetic typography in short-form product launches",
        "Neo-brutalist UI grid systems for high-converting landing pages",
        "Automated multi-agent brand identity prompt pipelines"
    ]

def generate_vault_entries(signals):
    """Calls Gemini Flash free API to convert raw signals into 3 structured Vault entries."""
    if not GEMINI_API_KEY:
        raise ValueError("Missing GEMINI_API_KEY environment variable.")

    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M")

    prompt = f"""You are an elite Creative Director, Brand Designer, Motion Artist, and AI Prompt Architect.
Based on these live industry signals from today ({today_str}):
{json.dumps(signals, indent=2)}

Generate EXACTLY 3 fresh, high-value entries for a paid Design, Motion & AI Prompt System Vault.
Return ONLY a valid JSON array of 3 objects with NO markdown fences and NO extra commentary.
Each object MUST use this exact schema:
{{
  "id": "vault-{stamp}-1",
  "date": "{today_str}",
  "title": "Specific, punchy system name (under 8 words)",
  "category": "One of: 'UI & Layout' | 'Motion & 3D' | 'Typography & Brand' | 'AI Prompt Workflow'",
  "trend_signal": "2-sentence concrete teardown explaining why this visual or workflow pattern performs and converts.",
  "typography_pairing": "Exact display font + body/mono font pairing recommendation",
  "color_palette": ["#HEX1", "#HEX2", "#HEX3", "#HEX4"],
  "pro_prompt_system": "Detailed, copy-pasteable 45-to-70-word production prompt or motion/design spec sheet that a creator can use immediately.",
  "is_pro_vault": false
}}
Make the first item have "is_pro_vault": false (Free Daily Hook), and the second and third items have "is_pro_vault": true (Locked Pro Vault). Ensure each ID ends with -1, -2, and -3."""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.8,
            "responseMimeType": "application/json"
        }
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        raw_text = result["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(raw_text)

def main():
    signals = fetch_live_signals()
    new_entries = generate_vault_entries(signals)

    existing = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            existing = json.load(f)

    # Prepend newest items at the top, keep up to 300 items
    updated = new_entries + existing
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(updated[:300], f, indent=2, ensure_ascii=False)

    print(f"Successfully added {len(new_entries)} new vault systems. Total in vault: {len(updated[:300])}")

if __name__ == "__main__":
    main()
