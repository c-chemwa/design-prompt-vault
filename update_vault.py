import os
import json
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from xml.sax.saxutils import escape

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
DATA_FILE = "data.json"
SITE_URL = "https://c-chemwa.github.io/design-prompt-vault"

def fetch_live_signals():
    """Pulls live design, frontend, and AI workflow signals from free public JSON APIs."""
    signals = []
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

def build_rss_and_sitemap(items):
    """Auto-generates feed.xml (for automated social posting) and sitemap.xml (for Google SEO)."""
    now_rfc = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    today_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    rss_items = []
    for item in items[:20]:
        title = escape(f"[{item['category']}] {item['title']}")
        palette_str = " ".join(item.get("color_palette", []))
        if item.get("is_pro_vault"):
            desc = escape(f"{item['trend_signal']} | Palette: {palette_str} | Unlock full Typography & Production Prompt Spec in SYS//VAULT ($19).")
        else:
            desc = escape(f"{item['trend_signal']} | Fonts: {item['typography_pairing']} | Palette: {palette_str} | Prompt: {item['pro_prompt_system']}")
        link = f"{SITE_URL}/?id={escape(item['id'])}"
        rss_items.append(f"""    <item>
      <title>{title}</title>
      <link>{link}</link>
      <guid isPermaLink="false">{escape(item['id'])}</guid>
      <description>{desc}</description>
    </item>""")

    rss_xml = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
  <channel>
    <title>SYS//VAULT — Daily Design, Motion &amp; AI Prompt Systems</title>
    <link>{SITE_URL}/</link>
    <description>Autonomous daily radar of UI layouts, 60fps motion specs, typography pairings, and AI prompt systems.</description>
    <lastBuildDate>{now_rfc}</lastBuildDate>
{chr(10).join(rss_items)}
  </channel>
</rss>"""

    with open("feed.xml", "w", encoding="utf-8") as f:
        f.write(rss_xml)

    sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{SITE_URL}/</loc>
    <lastmod>{today_iso}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>"""

    with open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write(sitemap_xml)

def main():
    signals = fetch_live_signals()
    new_entries = generate_vault_entries(signals)

    existing = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            existing = json.load(f)

    updated = new_entries + existing
    final_list = updated[:300]

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(final_list, f, indent=2, ensure_ascii=False)

    build_rss_and_sitemap(final_list)
    print(f"Updated data.json ({len(final_list)} items), feed.xml, and sitemap.xml")

if __name__ == "__main__":
    main()
