import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def generate_route_explanation(routes):
    """
    routes: list of route dicts, each with distance_meters, duration_seconds,
            and lighting (lit_percent, unlit_percent, unknown_percent)

    Returns a plain-language explanation comparing the routes.
    """
    if not routes:
        return "No routes available to compare."

    if len(routes) == 1:
        r = routes[0]
        summary = _describe_route(r)
        prompt = f"""You are a safety-focused route advisor for a night-time navigation app.
Describe this single route to a rider in 1-2 short, plain sentences, focusing on safety (lighting) and practicality (time/distance).

Route: {summary}

Keep it conversational and concise. Do not use markdown formatting."""
    else:
        summaries = "\n".join([f"Route {i+1}: {_describe_route(r)}" for i, r in enumerate(routes)])
        prompt = f"""You are a safety-focused route advisor for a night-time navigation app.
Compare these route options for a rider, focusing on the trade-off between safety (street lighting) and practicality (time/distance).
Recommend which one seems best and briefly explain why, in 2-3 short, plain sentences.

{summaries}

Keep it conversational and concise. Do not use markdown formatting."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=150,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"AI explanation unavailable right now ({str(e)})."


def _describe_route(route):
    minutes = round(route.get("duration_seconds", 0) / 60)
    km = round(route.get("distance_meters", 0) / 1000, 1)
    lighting = route.get("lighting", {})

    if lighting.get("unavailable"):
        lighting_desc = "lighting data unavailable"
    else:
        lit = lighting.get("lit_percent", 0)
        unlit = lighting.get("unlit_percent", 0)
        unknown = lighting.get("unknown_percent", 0)
        lighting_desc = f"{lit}% well-lit, {unlit}% unlit, {unknown}% unknown lighting"

    return f"{minutes} min, {km} km, {lighting_desc}"