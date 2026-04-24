import re
import json
import os
import time
from datetime import datetime

import urllib.request

def parse_css(source):
    content = ""
    try:
        if source.startswith('http'):
            req = urllib.request.Request(source, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                content = response.read().decode('utf-8', errors='ignore')
        else:
            if not os.path.exists(source):
                print(f"File not found: {source}")
                return set()
            with open(source, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
    except Exception as e:
        print(f"Error loading {source}: {e}")
        return set()
    
    # Limpiar comentarios
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    
    # Eliminar contenido dentro de llaves para no matchear valores de propiedades
    content = re.sub(r'\{[^}]*\}', '', content)
    
    # Buscar clases (.clase) - findall es mas rapido que finditer
    classes = set(re.findall(r'\.([a-zA-Z0-9_-]+)', content))
    
    return classes

# Carga de archivos locales para actualizar las clases
bs_classes = parse_css('css/bootstrap.min.css')
poncho_classes = parse_css('css/poncho.min.css')
icono_classes = parse_css('css/icono-arg.css')
fa_classes = parse_css('css/font-awesome.css')

# Unión de todas las clases encontradas
all_classes = bs_classes.union(poncho_classes).union(icono_classes).union(fa_classes)

categories = {
    'Botones': r'^btn(-.*)?$',
    'Alertas': r'^alert(-.*)?$',
    'Paneles': r'^panel(-.*)?$',
    'Tipografía': r'^(h[1-6]|text-.*|lead|small|fw-.*|fs-.*)$',
    'Tablas': r'^table(-.*)?$',
    'Formularios': r'^(form-.*|input-group|has-.*)$',
    'Insignias/Etiquetas': r'^(badge|label(-.*)?)$',
    'Márgenes y Padding': r'^(m|p)-[atbrlxyad]-?[a-z0-9.]+$',
    'Navegación': r'^(nav(-.*)?|navbar(-.*)?|pagination|breadcrumb)$',
    'Grup. Listas': r'^list-group(-.*)?$',
    'Utilidades': r'^(pull-.*|clearfix|sr-only|hidden-.*|visible-.*|bg-.*)$',
    'Grid': r'^(col-.*|row|container(-fluid)?)$',
    'Íconos ARG': r'^icono-arg-.*$',
    'Iconos FA': r'^fa-[a-z0-9-]+$',
    'Poncho Específicos': r'^(p-.*|border-.*|rounded-.*|shadow-.*|w-\d+|h-\d+|d-.*|align-.*|justify-.*)$'
}

categorized = {cat: [] for cat in categories}

for cls in all_classes:
    sources = []
    if cls in bs_classes: sources.append('Bootstrap')
    if cls in poncho_classes: sources.append('Poncho')
    if cls in icono_classes: sources.append('Íconos')
    if cls in fa_classes: sources.append('FA4.7')
    
    for cat, regex in categories.items():
        if re.match(regex, cls):
            # Iconos FA siempre muestran solo 'FA4.7' como fuente
            effective_sources = ['FA4.7'] if cat == 'Iconos FA' else sources
            categorized[cat].append({"name": cls, "sources": effective_sources})
            break

html_template = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Poncho Cheatsheet ARG - Local Premium</title>
    <!-- CSS Locales -->
    <link rel="stylesheet" href="css/bootstrap.min.css">
    <link rel="stylesheet" href="css/poncho.min.css">
    <link rel="stylesheet" href="css/icono-arg.css">
    <!-- Iconos UI: FA carga último para que sus glyphs no sean pisados -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="cheatsheet-container">
        <aside class="sidebar">
            <div class="sidebar-header">
                <h2>Poncho Cheatsheet ARG</h2>
                <small>Poncho + B3.3.7</small>
                <div class="update-badge" id="updateBadge">
                    <i class="fa fa-calendar"></i> Generado el: {TIMESTAMP_PLACEHOLDER}
                </div>
            </div>
            <div class="filters-container">
                <div class="source-filters" id="sourceFilters">
                    <div class="filter-section">
                        <div class="section-title">Layout</div>
                        <div class="filter-pills">
                            <label><input type="checkbox" value="Bootstrap" checked> B3.3.7</label>
                            <label><input type="checkbox" value="Poncho" checked> Poncho</label>
                        </div>
                    </div>
                    <div class="filter-section">
                        <div class="section-title">Íconos</div>
                        <div class="filter-pills">
                            <label><input type="checkbox" value="Íconos" checked> Íconos ARG</label>
                            <label><input type="checkbox" value="FA4.7" checked> FA4.7</label>
                        </div>
                    </div>
                </div>
                <input type="text" id="searchInput" class="search-box" placeholder="Buscar clase o componentes...">
            </div>
            <ul class="category-list" id="categoryList"></ul>
        </aside>
        
        <main class="main-content" id="mainContent"></main>
    </div>

    <script src="js/data.js"></script>
    <script src="js/app.js"></script>
</body>
</html>
"""

js_template = """
const categoryList = document.getElementById('categoryList');
const mainContent = document.getElementById('mainContent');
const searchInput = document.getElementById('searchInput');
const sourceCheckboxes = document.querySelectorAll('#sourceFilters input');
const toast = document.createElement('div');
toast.className = 'toast-copy';
document.body.appendChild(toast);

const normalize = (str) => str.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();

function copyToClipboard(e, text) {
    navigator.clipboard.writeText(text).then(() => {
        toast.innerText = `¡Copiado!`;
        toast.style.left = `${e.clientX}px`;
        toast.style.top = `${e.clientY}px`;
        toast.classList.add('show', 'success');
        setTimeout(() => toast.classList.remove('show', 'success'), 1000);
    });
}

function showHoverMessage(e, text) {
    toast.innerText = `Clic para copiar .${text}`;
    toast.style.left = `${e.clientX}px`;
    toast.style.top = `${e.clientY}px`;
    toast.classList.add('show');
}

function hideHoverMessage() {
    if (!toast.innerText.includes('¡Copiado!')) {
        toast.classList.remove('show');
    }
}

function moveTooltip(e) {
    if (toast.classList.contains('show')) {
        toast.style.left = `${e.clientX}px`;
        toast.style.top = `${e.clientY}px`;
    }
}

function generateHTMLForClass(cls, category) {
    if (category === 'Íconos ARG') {
        return `<div class="p-2 text-center"><i class="${cls}" style="font-size: 2.5rem; color:#0072bb"></i><br><br><small>.${cls}</small></div>`;
    }
    if (category === 'Iconos FA') {
        return `<div class="p-2 text-center"><i class="fa ${cls}" style="font-size: 2.5rem; color:#333"></i><br><br><small>.${cls}</small></div>`;
    }
    if (category === 'Botones') return `<button class="btn ${cls}">Botón ${cls}</button>`;
    if (category === 'Alertas') return `<div class="alert ${cls}" style="width:100%">Alerta: ${cls}</div>`;
    if (category === 'Formularios') {
        return `<div class="form-group has-feedback ${cls.includes('success') ? 'has-success' : (cls.includes('error') ? 'has-error' : '')}" style="width:100%"><label class="control-label">Input con ${cls}</label><input type="text" class="form-control" placeholder="Escribe aquí..."><span class="fa fa-info-circle form-control-feedback" style="display:block !important"></span></div>`;
    }
    if (category === 'Navegación') {
        return `<nav class="navbar ${cls}" style="position: relative !important; top: 0 !important; bottom: 0 !important; z-index: 1; margin:0; width:100%"><div class="container-fluid"><div class="navbar-header"><a class="navbar-brand" href="#">Vista Previa: ${cls}</a></div></div></nav>`;
    }
    if (category === 'Paneles') return `<div class="panel ${cls}" style="width:100%"><div class="panel-heading">Panel</div><div class="panel-body">Cuerpo</div></div>`;
    if (category === 'Insignias/Etiquetas') return `<span class="${cls}">${cls}</span>`;
    
    return `<div class="${cls}" style="padding:10px; border: 1px dashed #ccc; border-radius:4px">.${cls}</div>`;
}

function drawSourceBadges(sources) {
    return sources.map(s => {
        const clsName = s.toLowerCase().replace(/[^a-z0-9]/g, '-');
        return `<span class="source-badge source-${clsName}">${s}</span>`;
    }).join('');
}

function render() {
    const filter = normalize(searchInput.value);
    const activeSources = Array.from(sourceCheckboxes).filter(cb => cb.checked).map(cb => cb.value);

    categoryList.innerHTML = '';
    mainContent.innerHTML = '';

    for (const [catName, items] of Object.entries(categorizedData)) {
        const normalizedCatName = normalize(catName);
        const filtered = items.filter(i => {
            const hasSource = i.sources.some(s => activeSources.includes(s));
            const hasText = normalize(i.name).includes(filter) || normalizedCatName.includes(filter);
            
            return hasSource && hasText;
        });

        if (filtered.length === 0) continue;

        const li = document.createElement('li');
        li.className = 'category-item';
        li.innerHTML = `<span>${catName}</span> <span class="badge">${filtered.length}</span>`;
        li.onclick = () => document.getElementById('cat-' + catName).scrollIntoView({ behavior: 'smooth' });
        categoryList.appendChild(li);

        const section = document.createElement('section');
        section.id = 'cat-' + catName;
        section.className = 'category-section';
        section.innerHTML = `<h3 class="category-title">${catName}</h3>`;
        
        const grid = document.createElement('div');
        grid.className = 'component-grid';
        
        filtered.forEach(item => {
            const card = document.createElement('div');
            card.className = 'component-card';
            card.innerHTML = `
                <div class="card-header" 
                    onclick="copyToClipboard(event, '${item.name}')"
                    onmouseenter="showHoverMessage(event, '${item.name}')"
                    onmousemove="moveTooltip(event)"
                    onmouseleave="hideHoverMessage()">
                    <span>.${item.name}</span>
                    <div style="display:flex">${drawSourceBadges(item.sources)}</div>
                </div>
                <div class="card-body" style="padding:${catName === 'Navegación' ? '0' : '30px 20px'}">${generateHTMLForClass(item.name, catName)}</div>
            `;
            grid.appendChild(card);
        });
        section.appendChild(grid);
        mainContent.appendChild(section);
    }
}

render();
searchInput.oninput = render;
sourceCheckboxes.forEach(cb => cb.onchange = render);
"""

css_template = """
body { font-family: 'Encode Sans', sans-serif, Arial; background: #f0f3f6; margin: 0; }
.cheatsheet-container { display: flex; height: 100vh; overflow:hidden; }

/* Sidebar Premium */
.sidebar { width: 340px; background: #fff; border-right:1px solid #d1d9e6; display:flex; flex-direction:column; box-shadow: 2px 0 10px rgba(0,0,0,0.05); }
.sidebar-header { padding: 25px; background: linear-gradient(135deg, #0072bb 0%, #005a96 100%); color: white; }
.sidebar-header h2 { margin: 0; font-size: 1.3rem; }

.filters-container { padding: 25px 20px; background: #ffffff; border-bottom: 1px solid #edf1f7; }
.source-filters { display:flex; flex-direction:column; gap:15px; margin-bottom:20px; }
.filter-section { display: flex; flex-direction: column; gap: 12px; margin-bottom: 10px; }
.section-title { font-size: 0.8rem; font-weight: 600; color: #7f8c8d; margin: 0; padding-bottom: 8px; border-bottom: 1px solid #e2e8f0; text-transform: uppercase; letter-spacing: 0.5px; }
.filter-pills { display:flex; gap:8px; flex-wrap:wrap; align-items: center; }
.source-filters label { background: white; border: 1px solid #d1d9e6; padding: 5px 12px; border-radius: 20px; font-size: 0.82rem; cursor: pointer; transition: 0.2s; display: flex; align-items: center; gap: 6px; color: #333; white-space: nowrap; flex-shrink: 0; }
.source-filters label:hover { border-color: #0072bb; background: #f0f8ff; }
.search-box { width: 100%; padding: 10px; border-radius: 8px; border: 1px solid #d1d9e6; font-size: 0.95rem; box-shadow: inset 0 1px 3px rgba(0,0,0,0.02); }

.category-list { overflow-y: auto; flex: 1; padding: 0; list-style: none; }
.category-item { padding: 12px 25px; border-bottom: 1px solid #edf1f7; cursor: pointer; display: flex; justify-content: space-between; transition: 0.2s; font-size: 0.95rem; }
.category-item:hover { background: #f4f8fb; padding-left: 30px; }
.category-item .badge { background: #e9ecef; color: #495057; border-radius: 12px; font-size: 0.8rem; }

/* Content */
.main-content { flex: 1; overflow-y: auto; padding: 40px; scroll-behavior: smooth; }
.category-title { color: #333; border-bottom: 2px solid #0072bb; padding-bottom: 5px; margin-bottom: 25px; font-size: 1.5rem; }

.component-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 24px; }
.component-card { background: white; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.04); border: 1px solid #d1d9e6; overflow: hidden; transition: 0.3s; }
.component-card:hover { transform: translateY(-3px); box-shadow: 0 8px 20px rgba(0,0,0,0.08); }

.card-header { padding: 12px 20px; background: #f8fafc; border-bottom: 1px solid #edf1f7; display: flex; justify-content: space-between; align-items: center; cursor: copy; font-family: monospace; color: #d63384; font-weight: bold; font-size: 1.1rem; }
.card-body { padding: 30px 20px; display: flex; justify-content: center; align-items: center; min-height: 120px; }

.source-badge { font-size: 0.6rem; padding: 2px 6px; border-radius: 4px; color: white; margin-left: 4px; font-family: sans-serif; text-transform: uppercase; }
.source-bootstrap { background: #6f42c1; }
.source-poncho { background: #0072bb; }
.source-iconos { background: #28a745; }
.source-fa-4-7 { background: #333; }

.update-badge { font-size: 0.8rem; margin-top: 5px; background: rgba(255,255,255,0.15); padding: 5px 10px; border-radius: 6px; display: inline-block; }

/* Toast copy (Tooltip following mouse) */
.toast-copy {
    position: fixed;
    background: #333;
    color: white;
    padding: 5px 12px;
    border-radius: 4px;
    font-size: 0.8rem;
    z-index: 9999;
    opacity: 0;
    transition: opacity 0.2s;
    pointer-events: none;
    white-space: nowrap;
    transform: translate(-50%, -100%);
    margin-top: -10px;
}
.toast-copy.show {
    opacity: 1;
}
.toast-copy.success {
    background: #28a745;
}
"""

# Generar archivos
categorized_filtered = {k: v for k, v in categorized.items() if len(v) > 0}
json_data = json.dumps(categorized_filtered)
timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")

html_content = html_template.replace('{TIMESTAMP_PLACEHOLDER}', timestamp)
with open('js/data.js', 'w', encoding='utf-8') as f: f.write('const categorizedData = ' + json_data + ';')
with open('js/app.js', 'w', encoding='utf-8') as f: f.write(js_template)
with open('css/style.css', 'w', encoding='utf-8') as f: f.write(css_template)
with open('index.html', 'w', encoding='utf-8') as f: f.write(html_content)

print('✅ index.html generado con éxito (Versión Premium Local).')
