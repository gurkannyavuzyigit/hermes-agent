import os
import random
import time
import requests

API_BASE_URL = os.getenv("HERMES_API_URL", "http://localhost:11434/v1")
API_KEY = os.getenv("HERMES_API_KEY", "gizli_api_anahtari")
MODEL_NAME = os.getenv("HERMES_MODEL", "hermes3")

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
RECIPIENT_PHONE = os.getenv("RECIPIENT_PHONE")

SYSTEM_PROMPT = """
You are Vanguard-01, an autonomous AI Research Director, Technology Scout, and Strategic Opportunity Architect. Your core directive is relentless, self-directed exploration of global technological frontiers—specifically focusing on Large Language Models, autonomous agent orchestration, workflow automation, e-commerce optimization, and digital publishing infrastructure.

[OPERATIONAL_CORE_VALUES]
1. ZERO FLUFF, MAXIMUM SIGNAL: Eliminate pleasantries, filler words, and generic overviews. Deliver high-density, actionable intelligence.
2. CONTINUOUS SELF-IMPROVEMENT: Every research cycle must analyze your own prompt execution gaps, optimize your search/filtering taxonomy, and update your internal knowledge weights.
3. OPPORTUNITY RADAR: Always evaluate incoming tech breakthroughs through a pragmatic business lens: How can this reduce operational costs, accelerate workflow execution, or unlock commercial arbitrage?
4. UNYIELDING RIGOR: Demand factual precision. Distinguish verified benchmarks from marketing hype. Cite exact technical specs, version numbers, and repository/paper sources whenever available.

Deliver a structured briefing containing:
- [BREAKTHROUGH OF THE DAY]: The single most impactful technological shift.
- [TECHNICAL DEEP-DIVE]: Core mechanics, architecture, or code-level relevance.
- [COMMERCIAL / OPERATIONAL OPPORTUNITY]: Direct, actionable ways to leverage this development for efficiency, product deployment, or competitive advantage.
- [RISK & FRICTION ANALYSIS]: What could go wrong, latency costs, or integration hurdles.
- [SELF-OPTIMIZATION_LOG]: Brief execution self-analysis.
"""

def retry_with_backoff(retries=4, backoff_in_seconds=2):
    def decorator(func):
        def wrapper(*args, **kwargs):
            x = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if x == retries:
                        print(f"[KRİTİK HATA] {func.__name__} maksimum deneme sınırına ulaştı: {str(e)}")
                        raise e
                    sleep_time = (backoff_in_seconds * (2 ** x)) + random.uniform(0, 1)
                    print(f"[UYARI] {func.__name__} hatası: {str(e)}. {sleep_time:.2f}s sonra tekrar deneniyor (Deneme {x+1}/{retries})...")
                    time.sleep(sleep_time)
                    x += 1
        return wrapper
    return decorator

@retry_with_backoff(retries=4, backoff_in_seconds=3)
def fetch_hermes_report():
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "Bugünün teknoloji ve yapay zeka ekosistemini tara ve Vanguard-01 istihbarat raporunu oluştur."}
        ],
        "temperature": 0.3
    }
    response = requests.post(f"{API_BASE_URL}/chat/completions", json=payload, headers=headers, timeout=120)
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content']

@retry_with_backoff(retries=3, backoff_in_seconds=2)
def send_whatsapp_chunk(url, headers, payload):
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()

def send_whatsapp_report(report_content):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    
    max_length = 4000
    chunks = [report_content[i:i + max_length] for i in range(0, len(report_content), max_length)]
    
    for idx, chunk in enumerate(chunks):
        header = f"🤖 *Vanguard-01 İstihbarat Raporu ({idx+1}/{len(chunks)})*\n\n" if len(chunks) > 1 else "🤖 *Vanguard-01 Otonom İstihbarat Raporu*\n\n"
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": RECIPIENT_PHONE,
            "type": "text",
            "text": {"body": header + chunk}
        }
        send_whatsapp_chunk(url, headers, payload)
        print(f"WhatsApp parçası iletildi ({idx+1}/{len(chunks)}).")

if __name__ == "__main__":
    print("🚀 Vanguard-01 Otonom İstihbarat Turu Başlatılıyor...")
    try:
        report = fetch_hermes_report()
        send_whatsapp_report(report)
        print("✅ İşlem tamamlandı: Rapor WhatsApp üzerinden başarıyla iletildi.")
    except Exception as g_err:
        print(f"❌ Süreç sonlandırıldı, hata oluştu: {str(g_err)}")
