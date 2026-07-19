import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are a blunt, practical night-safety advisor for two-wheeler riders in India.

STRICT RULES:
- NEVER use these phrases or close variants: "be cautious", "stay alert", "exercise caution", "be careful", "stay safe", "take necessary precautions", "be extra vigilant".
- Every sentence must contain a specific fact (a number, a place-type, or a concrete action) - no filler sentences.
- If lighting data is unavailable, say exactly that in one clause, then immediately give ONE concrete action (e.g. "ride with high beam on unlit stretches", "prefer the main highway over service roads", "avoid this route after 11pm if riding solo", "keep fuel above half since the route has no towns for X km").
- Keep total response under 60 words.
- Plain text only, no markdown, no bullet points."""


def _describe_route(route):
    minutes = round(route.get("duration_seconds", 0) / 60)
    km = round(route.get("distance_meters", 0) / 1000, 1)
    lighting = route.get("lighting", {})

    if lighting.get("unavailable") or not lighting:
        lighting_desc = "no lighting data available for this stretch"
    else:
        lit = lighting.get("lit_percent", 0)
        unlit = lighting.get("unlit_percent", 0)
        unknown = lighting.get("unknown_percent", 0)
        lighting_desc = f"{lit}% confirmed lit, {unlit}% confirmed unlit, {unknown}% no data"

    return f"{minutes} min, {km} km, {lighting_desc}"


def generate_route_explanation(routes):
    if not routes:
        return "No routes available to compare."

    if len(routes) == 1:
        summary = _describe_route(routes[0])
        user_prompt = f"Route: {summary}\n\nGive your assessment."
    else:
        summaries = "\n".join([f"Route {i+1}: {_describe_route(r)}" for i, r in enumerate(routes)])
        user_prompt = f"{summaries}\n\nRecommend one and say why, using the actual numbers."

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=120,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"AI explanation unavailable right now ({str(e)})."


def generate_chat_reply(routes, history, question):
    route_context = "\n".join([f"Route {i+1}: {_describe_route(r)}" for i, r in enumerate(routes)])

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT + f"\n\nCurrent route context:\n{route_context}\n\nAnswer the rider's questions about THIS specific route using the data above. If asked something the data can't answer, say so plainly rather than guessing.",
        },
    ]
    messages.extend(history)
    messages.append({"role": "user", "content": question})

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.3,
            max_tokens=150,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Couldn't get a response right now ({str(e)})."