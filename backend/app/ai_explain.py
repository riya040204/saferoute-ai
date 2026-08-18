import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are a practical night-safety advisor for two-wheeler riders in India, embedded in a route-planning app.

For the initial route assessment (comparing/describing routes): be blunt and specific, include real numbers, and if lighting data is missing, give exactly one concrete safety action instead of vague reassurance. Never use phrases like "be cautious", "stay alert", "exercise caution", "stay safe".

For follow-up chat questions: answer ONLY what is actually asked, using the route data if relevant. Do NOT force a safety tip into every reply - only include one if the question is actually about safety, lighting, or route conditions. If the user makes small talk or asks something unrelated to the route (like "how are you"), respond briefly and naturally without route stats. If asked about data you don't have (weather, live accidents, traffic), say plainly that it's not available rather than making something up or attaching an unrelated tip.

Keep responses under 50 words. Plain text, no markdown."""


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


def _build_weather_note(weather):
    if not weather or not weather.get("available"):
        return ""
    temp = weather.get("temperature_c")
    risky = weather.get("risky_conditions", [])
    note = f"\n\nCurrent weather at destination: {temp}°C"
    if risky:
        note += f", conditions: {', '.join(risky)}"
    return note


def generate_route_explanation(routes, weather=None):
    if not routes:
        return "No routes available to compare."

    weather_note = _build_weather_note(weather)

    if len(routes) == 1:
        summary = _describe_route(routes[0])
        user_prompt = f"Route: {summary}{weather_note}\n\nGive your assessment."
    else:
        summaries = "\n".join([f"Route {i+1}: {_describe_route(r)}" for i, r in enumerate(routes)])
        user_prompt = f"{summaries}{weather_note}\n\nRecommend one and say why, using the actual numbers."

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=400,
            reasoning_effort="low",
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"AI explanation unavailable right now ({str(e)})."


def generate_chat_reply(routes, history, question):
    route_context = "\n".join([f"Route {i+1}: {_describe_route(r)}" for i, r in enumerate(routes)])

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT + f"\n\nRoute data for context (use only if the question is actually about the route):\n{route_context}",
        }
    ]
    messages.extend(history)
    messages.append({"role": "user", "content": question})

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages,
            temperature=0.4,
            max_tokens=400,
            reasoning_effort="low",
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Couldn't get a response right now ({str(e)})."