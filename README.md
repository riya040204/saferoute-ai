# SafeRoute AI 🌙🚦

AI-powered real-time **night safety routing** for two-wheeler riders and solo commuters in India.

**Live demo:** https://saferoute-ai-eight.vercel.app
**API docs:** https://saferoute-ai-backend-jymm.onrender.com/docs

## The Problem
Google Maps and other navigation apps optimize purely for speed or distance. They have no concept of whether a route is well-lit, populated, or has a history of safety incidents — factors that matter enormously for solo riders, women commuting after dark, and students traveling alone at night.

## What SafeRoute AI Does
Given a start and end point, SafeRoute AI compares route options not just on time/distance, but on a **safety score** built from real street lighting data, and layers in live weather and an AI safety advisor you can chat with about your specific route.

### Features
- 🔦 **Street lighting analysis** per route, via OpenStreetMap/Overpass data
- 🌧️ **Live weather conditions** at your destination (Open-Meteo)
- 🤖 **AI-generated safety recommendations** comparing route options (Groq/Llama)
- 💬 **Contextual chat** — ask follow-up questions about your specific route
- 📍 **Live GPS ride tracking** with real-time distance-to-destination
- 🗺️ **India-wide search** with GPS auto-location for your starting point
- 🌗 **Light/dark map modes**
- 🏍️ Travel mode selection (two-wheeler / car)

## Tech Stack
- **Backend**: FastAPI (Python), deployed on Render
- **Frontend**: React + Vite + Leaflet, deployed on Vercel
- **Routing**: OSRM
- **Geocoding**: Nominatim (OpenStreetMap)
- **AI**: Groq API (Llama-based models)
- **Weather**: Open-Meteo

## Architecture
