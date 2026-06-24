# Hospitais de Belém — Urgência e Emergência

Site de localização das unidades de **urgência e emergência de Belém/PA**: hospitais, prontos-socorros, UPAs e unidades municipais de saúde.

🔗 **Acesse:** https://iurivalente.github.io/hospitais-belem/

## Funcionalidades

- 🗺️ Mapa interativo (Leaflet + OpenStreetMap) com as 16 unidades, coloridas por tipo
- 🔎 Busca por nome ou bairro (ignora acentuação)
- 🏷️ Filtros por tipo (Hospital / UPA / Unidade)
- 📍 "Perto de mim" (geolocalização) e 🧭 "Como chegar" (rota no Google Maps)
- 📱 Layout responsivo (mobile-first)

## Estrutura

- `index.html` — o site (arquivo único, autossuficiente, com os dados embutidos)
- `hospitais_belem.geojson` — os dados no formato GeoJSON
- `gerar_site.py` — script que gera o site a partir do arquivo KMZ de origem

## Dados

16 unidades de urgência e emergência de Belém/PA, com nome, endereço, bairro, perfil de atendimento e coordenadas geográficas.

---
Mapa © colaboradores do [OpenStreetMap](https://www.openstreetmap.org/copyright).
