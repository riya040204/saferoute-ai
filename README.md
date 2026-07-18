# SafeRoute AI 🌙🚦

AI-powered real-time **night safety routing** for two-wheeler riders and solo commuters.

## The Problem

Google Maps and other navigation apps optimize purely for speed or distance. They have no concept of whether a route is well-lit, populated, or has a history of safety incidents — factors that matter enormously for solo riders, women commuting after dark, and students traveling alone at night. Many riders manually choose longer, "safer-feeling" routes with no way to verify that choice.

## What SafeRoute AI Does

Given a start and end point, SafeRoute AI compares route options not just on time/distance, but on a **safety score** built from:

- 🔦 **Street lighting** (via OpenStreetMap tagging)
- 🏘️ **Population/activity density** nearby (isolated stretches score higher risk)
- 📊 **Historical incident data**
- 🌧️ **Live weather conditions**

An AI layer then explains the trade-off in plain language — e.g. _"This route stays on well-lit main roads but takes 4 minutes longer than the fastest option."_

## Status

🚧 Under active development

**Working:**

- Real-time routing via OSRM
- GPS-based starting location
- India-wide destination search
- Street lighting analysis along routes (via OpenStreetMap/Overpass)
- Graceful fallback when third-party data sources are unavailable

**Planned:**

- Historical incident data integration
- Time-of-day and weather-based risk scoring
- AI-generated route trade-off explanations

## Tech Stack

- **Backend**: FastAPI (Python)
- **Routing**: OSRM
- **Geo data**: OpenStreetMap / Overpass API / Nominatim
- **Frontend**: React + Leaflet
- **AI**: Risk scoring model + LLM-based explanations (coming soon)

## Getting Started

Instructions coming soon as the project develops.
