# Vue 3 + Vite

This project uses Vue 3 + Vite.

## Run locally

```bash
npm install
npm run dev
```

## Google Geocoding setup

The Discover page `Locate` button uses browser geolocation and Google Geocoding API.

1. Create an API key in Google Cloud Console.
2. Enable the **Geocoding API** for that key.
3. Add the key to a local env file:

```bash
cp .env.example .env.local
```

Then set:

```bash
VITE_GOOGLE_MAPS_API_KEY=your_real_key
```

Recommended: restrict the key by HTTP referrer and Geocoding API.
