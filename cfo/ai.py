"""AI adapter with a safe deterministic fallback when no provider is configured."""
import os, json, urllib.request, urllib.error

def _fallback(question, summary):
    q=question.lower()
    if any(x in q for x in ["profit","margin","earning"]):
        return (f"Recorded revenue is ₹{summary['revenue']:,.2f}, expenses are ₹{summary['expenses']:,.2f}, "
                f"and calculated profit is ₹{summary['profit']:,.2f}. Profit margin is {summary['margin']:.2f}%. "
                "Review account classifications and transaction completeness before acting.")
    if "cash" in q or "runway" in q:
        return (f"Net cash movement from entered transactions is ₹{summary['cash']:,.2f}. "
                "This is not a bank-confirmed balance. Add complete opening balances and future dated obligations "
                "for a reliable cash forecast.")
    if "forecast" in q or "scenario" in q:
        return "Create base, optimistic and pessimistic forecast records. Change revenue and expense assumptions, then compare projected profit and cash needs."
    return ("I can help analyze revenue, expenses, profitability, cash flow, budgets, risks and scenarios. "
            f"Current recorded revenue: ₹{summary['revenue']:,.2f}; expenses: ₹{summary['expenses']:,.2f}; "
            f"profit: ₹{summary['profit']:,.2f}. Ask a focused question for a more specific analysis.")

def copilot_answer(question, summary):
    key=os.getenv("AI_API_KEY")
    if not key:
        return _fallback(question, summary)
    # Send only the user's question and aggregate metrics, not transaction-level personal data.
    payload={"model":os.getenv("AI_MODEL","gpt-4o-mini"),"messages":[
      {"role":"system","content":"You are a cautious CFO assistant. Use only the supplied aggregate figures. Do not invent facts. State assumptions and advise human review for material decisions."},
      {"role":"user","content":json.dumps({"question":question,"validated_aggregates":{k:str(v) for k,v in summary.items() if k!="transactions"}})}
    ],"temperature":0.2}
    req=urllib.request.Request(os.getenv("AI_BASE_URL","https://api.openai.com/v1/chat/completions"),
      data=json.dumps(payload).encode(),headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"},method="POST")
    try:
        with urllib.request.urlopen(req,timeout=20) as response:
            data=json.loads(response.read().decode())
        return data["choices"][0]["message"]["content"]
    except Exception:
        return _fallback(question, summary)+" (External AI provider was unavailable; deterministic fallback used.)"

def ai_provider_status():
    return "External AI provider configured" if os.getenv("AI_API_KEY") else "Local deterministic CFO assistant active (no API key configured)"
