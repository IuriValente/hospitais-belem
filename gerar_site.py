# -*- coding: utf-8 -*-
"""Gera o site (index.html autossuficiente) de localizacao de hospitais de
Belem a partir do KMZ. Mobile-first: mapa Leaflet + busca + filtros + lista +
'perto de mim' + 'como chegar'. Dados embutidos inline (abre via file://)."""
import zipfile, re, json, sys, os
import xml.etree.ElementTree as ET
from html import unescape
sys.stdout.reconfigure(encoding="utf-8")

KMZ = r"C:\Users\iuri_\Downloads\urgencia e emergencia ajustado.kmz"
OUT_DIR = r"C:\Users\iuri_\Downloads\site-hospitais-belem"
os.makedirs(OUT_DIR, exist_ok=True)

SIGLAS = {"UPA", "DASAC", "DAICO", "SUS", "I", "II", "III", "IV"}
PREPOS = {"de", "da", "do", "das", "dos", "e"}
CORRECOES = [("SANTA CADA", "SANTA CASA"), ("PUBLICO", "PÚBLICO"), ("LATITUIDE", "LATITUDE")]


def humanizar(nome):
    for a, b in CORRECOES:
        nome = nome.replace(a, b)
    out = []
    for i, w in enumerate(nome.split()):
        wu = w.upper().strip(".")
        if wu in SIGLAS:
            out.append(w.upper())
        elif w.upper() in ("DR.", "DR"):
            out.append("Dr.")
        elif w.upper() in ("DRA.", "DRA"):
            out.append("Dra.")
        elif w.lower() in PREPOS and i > 0:
            out.append(w.lower())
        elif "'" in w or "’" in w:
            sep = "’" if "’" in w else "'"
            out.append(sep.join(part.capitalize() for part in w.split(sep)))
        elif "-" in w:
            out.append("-".join(part.capitalize() for part in w.split("-")))
        else:
            out.append(w.capitalize())
    return " ".join(out)


def folhas_td(html):
    if not html:
        return []
    tds = re.findall(r"<td[^>]*>([^<]*)</td>", html, re.IGNORECASE)
    return [unescape(t).strip() for t in tds if unescape(t).strip()]


def classificar(nome):
    n = nome.upper()
    if "UPA" in n:
        return "UPA"
    if ("HOSPITAL" in n or "PRONTO SOCORRO" in n or "FUNDAÇÃO" in n
            or "SANTA CASA" in n or "SANTA CADA" in n or "CLÍNICAS" in n):
        return "Hospital / Pronto-Socorro"
    return "Unidade Básica / Municipal"


z = zipfile.ZipFile(KMZ)
kml = [n for n in z.namelist() if n.lower().endswith(".kml")][0]
text = z.read(kml).decode("utf-8", "replace")
root = ET.fromstring(re.sub(r'\sxmlns="[^"]+"', "", text, count=1))

feats = []
for pm in root.iter("Placemark"):
    nm = pm.find("name")
    nome_raw = nm.text.strip() if (nm is not None and nm.text) else ""
    coords = pm.find(".//coordinates")
    if coords is None or not coords.text:
        continue
    lon, lat = [float(x) for x in coords.text.strip().split()[0].split(",")[:2]]
    tds = folhas_td(pm.find("description").text if pm.find("description") is not None else "")
    pares = tds[1:] if (tds and tds[0] == nome_raw) else tds
    crus = {}
    for i in range(0, len(pares) - 1, 2):
        crus[pares[i].upper().strip()] = pares[i + 1].strip()
    feats.append({
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [lon, lat]},
        "properties": {
            "nome": humanizar(nome_raw),
            "endereco": crus.get("ENDEREÇO", "").strip(),
            "bairro": humanizar(crus.get("BAIRRO", "")),
            "perfil": humanizar(crus.get("PERFIL_DE", "")),
            "tipo": classificar(nome_raw),
        },
    })

# ordena por tipo e nome
feats.sort(key=lambda f: (f["properties"]["tipo"], f["properties"]["nome"]))
geo = {"type": "FeatureCollection", "features": feats}

with open(os.path.join(OUT_DIR, "hospitais_belem.geojson"), "w", encoding="utf-8") as fp:
    json.dump(geo, fp, ensure_ascii=False, indent=2)

# ----------------------------- SITE -----------------------------
dados_js = json.dumps(geo, ensure_ascii=False)
HTML = r"""<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Hospitais de Belém | Urgência e Emergência</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',Roboto,Arial,sans-serif;background:#eef1f4;color:#222}
header{background:linear-gradient(135deg,#d32f2f,#9e1414);color:#fff;padding:12px 16px}
header h1{font-size:19px;display:flex;align-items:center;gap:8px}
header p{font-size:12.5px;opacity:.92;margin-top:2px}
#controles{background:#fff;padding:10px 12px;box-shadow:0 2px 5px rgba(0,0,0,.1);position:relative;z-index:600}
#busca{width:100%;padding:11px 12px;border:1px solid #dcdcdc;border-radius:9px;font-size:15px;outline:none}
#busca:focus{border-color:#d32f2f}
#filtros{display:flex;gap:8px;margin-top:9px;overflow-x:auto;padding-bottom:3px;-webkit-overflow-scrolling:touch}
#filtros button{flex:0 0 auto;border:1px solid #dcdcdc;background:#f6f6f6;border-radius:20px;padding:7px 14px;font-size:13px;cursor:pointer;white-space:nowrap}
#filtros button.ativo{background:#d32f2f;color:#fff;border-color:#d32f2f}
#btn-perto{background:#1565c0!important;color:#fff!important;border-color:#1565c0!important;font-weight:bold}
#conteudo{display:flex;flex-direction:column;height:calc(100vh - 138px)}
#map{height:44vh;width:100%;z-index:1}
#lista{flex:1;overflow-y:auto;padding:10px;display:flex;flex-direction:column;gap:10px;-webkit-overflow-scrolling:touch}
.card{background:#fff;border-radius:11px;padding:12px 13px;box-shadow:0 1px 3px rgba(0,0,0,.13);border-left:5px solid #ccc;cursor:pointer;transition:box-shadow .15s}
.card:active,.card:hover{box-shadow:0 3px 10px rgba(0,0,0,.2)}
.card.sel{box-shadow:0 0 0 2px #d32f2f,0 3px 10px rgba(0,0,0,.2)}
.badge{display:inline-block;color:#fff;font-size:10.5px;font-weight:bold;padding:2px 9px;border-radius:10px;margin-bottom:5px;letter-spacing:.3px}
.card h3{font-size:14.5px;line-height:1.25;margin:2px 0}
.card .end{font-size:12.5px;color:#555;margin:4px 0}
.card .perfil{font-size:12px;color:#777}
.card .dist{font-size:13px;color:#1565c0;font-weight:bold;margin-top:5px}
.btn-rota{display:inline-block;margin-top:9px;background:#2e7d32;color:#fff;text-decoration:none;padding:8px 13px;border-radius:8px;font-size:13px;font-weight:bold}
.vazio{text-align:center;color:#999;padding:34px 10px}
.leaflet-popup-content{font-size:13px;line-height:1.4}
@media(min-width:900px){
  #conteudo{flex-direction:row-reverse}
  #map{height:100%;flex:1}
  #lista{width:390px;flex:none;border-right:1px solid #e2e2e2}
}
</style>
</head>
<body>
<header>
  <h1>🏥 Hospitais de Belém</h1>
  <p>__TOTAL__ unidades de urgência e emergência · toque numa unidade para localizar</p>
</header>
<div id="controles">
  <input id="busca" placeholder="🔎 Buscar por nome ou bairro...">
  <div id="filtros">
    <button data-tipo="todos" class="ativo">Todos</button>
    <button data-tipo="Hospital / Pronto-Socorro">Hospitais</button>
    <button data-tipo="UPA">UPAs</button>
    <button data-tipo="Unidade Básica / Municipal">Unidades</button>
    <button id="btn-perto">📍 Perto de mim</button>
  </div>
</div>
<div id="conteudo">
  <div id="map"></div>
  <div id="lista"></div>
</div>
<script>
const dados = __DADOS__;
const CORES = {"Hospital / Pronto-Socorro":"#e53935","UPA":"#fb8c00","Unidade Básica / Municipal":"#43a047"};
const CURTO = {"Hospital / Pronto-Socorro":"HOSPITAL","UPA":"UPA","Unidade Básica / Municipal":"UNIDADE"};
let posUsuario=null, filtroTipo='todos', termo='';

const map=L.map('map').setView([-1.40,-48.45],11);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'&copy; OpenStreetMap'}).addTo(map);

function semAcento(s){return (s||'').normalize('NFD').replace(/[̀-ͯ]/g,'').toLowerCase();}
function haversine(a,b){const R=6371,dLat=(b[0]-a[0])*Math.PI/180,dLon=(b[1]-a[1])*Math.PI/180;
  const x=Math.sin(dLat/2)**2+Math.cos(a[0]*Math.PI/180)*Math.cos(b[0]*Math.PI/180)*Math.sin(dLon/2)**2;
  return R*2*Math.atan2(Math.sqrt(x),Math.sqrt(1-x));}

const todos=[];
const itens=dados.features.map((f,i)=>{
  const p=f.properties,c=f.geometry.coordinates,latlng=[c[1],c[0]];
  todos.push(latlng);
  const m=L.circleMarker(latlng,{radius:9,color:'#fff',weight:2,fillColor:CORES[p.tipo]||'#3388ff',fillOpacity:.95});
  m.bindPopup('<b>'+p.nome+'</b><br><small>'+CURTO[p.tipo]+'</small><br>'+(p.endereco||'')+(p.bairro?' — '+p.bairro:''));
  m.on('click',()=>selecionar(i,false));
  return {i,p,latlng,m,dist:null};
});
map.fitBounds(todos,{padding:[30,30]});
const elLista=document.getElementById('lista');

function visiveis(){return itens.filter(it=>{
  if(filtroTipo!=='todos'&&it.p.tipo!==filtroTipo)return false;
  if(termo&&!semAcento(it.p.nome+' '+it.p.bairro).includes(semAcento(termo)))return false;
  return true;});}

function aplicar(){
  const vis=visiveis(),set=new Set(vis.map(v=>v.i));
  itens.forEach(it=>{if(set.has(it.i))it.m.addTo(map);else map.removeLayer(it.m);});
  let lista=vis.slice();
  if(posUsuario)lista.sort((a,b)=>a.dist-b.dist);
  renderLista(lista);
}

function renderLista(lista){
  if(!lista.length){elLista.innerHTML='<div class="vazio">Nenhuma unidade encontrada.<br>Tente outro termo ou filtro.</div>';return;}
  elLista.innerHTML='';
  lista.forEach(it=>{const p=it.p;
    const card=document.createElement('div');
    card.className='card';card.dataset.i=it.i;card.style.borderLeftColor=CORES[p.tipo];
    card.innerHTML='<span class="badge" style="background:'+CORES[p.tipo]+'">'+CURTO[p.tipo]+'</span>'+
      '<h3>'+p.nome+'</h3>'+
      (p.endereco?'<p class="end">📍 '+p.endereco+(p.bairro?' — '+p.bairro:'')+'</p>':(p.bairro?'<p class="end">📍 '+p.bairro+'</p>':''))+
      (p.perfil?'<p class="perfil">🩺 '+p.perfil+'</p>':'')+
      (it.dist!=null?'<p class="dist">📏 a '+it.dist.toFixed(1)+' km de você</p>':'')+
      '<a class="btn-rota" target="_blank" rel="noopener" href="https://www.google.com/maps/dir/?api=1&destination='+it.latlng[0]+','+it.latlng[1]+'">Como chegar →</a>';
    card.addEventListener('click',e=>{if(e.target.closest('.btn-rota'))return;selecionar(it.i,true);});
    elLista.appendChild(card);
  });
}

function selecionar(i,fly){
  const it=itens[i];
  if(fly){map.flyTo(it.latlng,15,{duration:.6});}
  it.m.addTo(map).openPopup();
  document.querySelectorAll('.card').forEach(c=>c.classList.toggle('sel',c.dataset.i==i));
  const card=document.querySelector('.card[data-i="'+i+'"]');
  if(card)card.scrollIntoView({behavior:'smooth',block:'nearest'});
}

function pertoDeMim(){
  const btn=document.getElementById('btn-perto');
  if(!navigator.geolocation){alert('Geolocalização não suportada neste navegador.');return;}
  btn.textContent='⏳ Localizando...';
  navigator.geolocation.getCurrentPosition(pos=>{
    posUsuario=[pos.coords.latitude,pos.coords.longitude];
    itens.forEach(it=>it.dist=haversine(posUsuario,it.latlng));
    L.marker(posUsuario).addTo(map).bindPopup('📍 Você está aqui').openPopup();
    map.setView(posUsuario,13);
    btn.textContent='📍 Perto de mim';
    aplicar();
  },()=>{btn.textContent='📍 Perto de mim';
    alert('Não foi possível obter sua localização. Verifique a permissão de localização do navegador (e note que isso costuma exigir o site publicado em HTTPS).');
  },{enableHighAccuracy:true,timeout:10000});
}

document.getElementById('busca').addEventListener('input',e=>{termo=e.target.value.trim();aplicar();});
document.querySelectorAll('#filtros button[data-tipo]').forEach(b=>b.addEventListener('click',()=>{
  document.querySelectorAll('#filtros button[data-tipo]').forEach(x=>x.classList.remove('ativo'));
  b.classList.add('ativo');filtroTipo=b.dataset.tipo;aplicar();}));
document.getElementById('btn-perto').addEventListener('click',pertoDeMim);
aplicar();
</script>
</body>
</html>
"""
HTML = HTML.replace("__DADOS__", dados_js).replace("__TOTAL__", str(len(feats)))
with open(os.path.join(OUT_DIR, "index.html"), "w", encoding="utf-8") as fp:
    fp.write(HTML)

print("Unidades:", len(feats))
print("Nomes humanizados:")
for f in feats:
    print("  -", f["properties"]["nome"], "|", f["properties"]["bairro"], "|", f["properties"]["tipo"])
print("\nSite:", os.path.join(OUT_DIR, "index.html"))
