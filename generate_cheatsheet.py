import re
import json
import os
import time
from datetime import datetime

def parse_css(path):
    if not os.path.exists(path):
        return set()
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Limpiar comentarios
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    
    # Buscar clases (.clase)
    classes = set()
    for match in re.finditer(r'\.([a-zA-Z0-9_-]+)', content):
        classes.add(match.group(1))
    
    return classes

# Carga de archivos locales (Asegúrate de que existan en la carpeta css/)
bs_classes = parse_css('css/bootstrap.min.css')
poncho_classes = parse_css('css/poncho.min.css')
icono_classes = parse_css('css/icono-arg.css')

# Unión de todas las clases encontradas
all_classes = bs_classes.union(poncho_classes).union(icono_classes)

categories = {
    'Botones': r'^btn(-.*)?$',
    'Alertas': r'^alert(-.*)?$',
    'Paneles': r'^panel(-.*)?$',
    'Tipografía': r'^(h[1-6]|text-.*|lead|small|fw-.*|fs-.*)$',
    'Tablas': r'^table(-.*)?$',
    'Formularios': r'^(form-.*|input-group|has-.*)$',
    'Insignias/Etiquetas': r'^(badge|label(-.*)?)$',
    'Márgenes y Padding': r'^(m|p)[xy]?[tb]?[l]?[r]?-?\d+$',
    'Navegación': r'^(nav(-.*)?|navbar(-.*)?|pagination|breadcrumb)$',
    'Grup. Listas': r'^list-group(-.*)?$',
    'Utilidades': r'^(pull-.*|clearfix|sr-only|hidden-.*|visible-.*|bg-.*)$',
    'Grid': r'^(col-.*|row|container(-fluid)?)$',
    'Íconos ARG': r'^icono-arg-.*$',
    'Poncho Específicos': r'^(p-.*|border-.*|rounded-.*|shadow-.*|w-\d+|h-\d+|d-.*|align-.*|justify-.*)$'
}

categorized = {cat: [] for cat in categories}

for cls in all_classes:
    sources = []
    if cls in bs_classes: sources.append('Bootstrap')
    if cls in poncho_classes: sources.append('Poncho')
    if cls in icono_classes: sources.append('Íconos')
    
    for cat, regex in categories.items():
        if re.match(regex, cls):
            categorized[cat].append({"name": cls, "sources": sources})
            break

html_template = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Poncho Cheatsheet ARG - Local Premium</title>
    <!-- CSS Locales -->
    <link rel="stylesheet" href="css/bootstrap.min.css">
    <link rel="stylesheet" href="css/icono-arg.css">
    <link rel="stylesheet" href="css/poncho.min.css">
    <link rel="stylesheet" href="css/style.css">
    <!-- Iconos UI -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
</head>
<body>
    <div class="cheatsheet-container">
        <aside class="sidebar">
            <div class="sidebar-header">
                <h2>Poncho Cheatsheet ARG</h2>
                <small>Poncho + Bootstrap 3</small>
                <div class="update-badge" id="updateBadge">
                    <i class="fa fa-calendar"></i> Generado el: {TIMESTAMP_PLACEHOLDER}
                </div>
            </div>
            <div class="filters-container">
                <div class="source-filters" id="sourceFilters">
                    <label><input type="checkbox" value="Bootstrap" checked> BS3</label>
                    <label><input type="checkbox" value="Poncho" checked> Poncho</label>
                    <label><input type="checkbox" value="Íconos" checked> Íconos</label>
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

function generateHTMLForClass(cls, category) {
    if (category === 'Íconos ARG') {
        return `<div class="p-2 text-center"><i class="${cls}" style="font-size: 2.5rem; color:#0072bb"></i><br><br><small>.${cls}</small></div>`;
    }
    if (category === 'Botones') return `<button class="btn ${cls}">Botón ${cls}</button>`;
    if (category === 'Alertas') return `<div class="alert ${cls}" style="width:100%">Alerta: ${cls}</div>`;
    if (category === 'Navegación') {
        return `<nav class="navbar ${cls}" style="margin:0; width:100%"><div class="container-fluid"><div class="navbar-header"><a class="navbar-brand" href="#">${cls}</a></div></div></nav>`;
    }
    if (category === 'Paneles') return `<div class="panel ${cls}" style="width:100%"><div class="panel-heading">Panel</div><div class="panel-body">Cuerpo</div></div>`;
    if (category === 'Insignias/Etiquetas') return `<span class="${cls}">${cls}</span>`;
    
    return `<div class="${cls}" style="padding:10px; border: 1px dashed #ccc; border-radius:4px">.${cls}</div>`;
}

function drawSourceBadges(sources) {
    return sources.map(s => `<span class="source-badge source-${s.toLowerCase()}">${s}</span>`).join('');
}

function render() {
    const filter = searchInput.value.toLowerCase();
    const activeSources = Array.from(sourceCheckboxes).filter(cb => cb.checked).map(cb => cb.value);

    categoryList.innerHTML = '';
    mainContent.innerHTML = '';

    for (const [catName, items] of Object.entries(categorizedData)) {
        const filtered = items.filter(i => {
            const hasSource = i.sources.some(s => activeSources.includes(s));
            const hasText = i.name.toLowerCase().includes(filter);
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
                <div class="card-header" onclick="navigator.clipboard.writeText('${item.name}')">
                    <span>.${item.name}</span>
                    <div style="display:flex">${drawSourceBadges(item.sources)}</div>
                </div>
                <div class="card-body" style="padding:${catName === 'Navegación' ? '0' : '15px'}">${generateHTMLForClass(item.name, catName)}</div>
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
.sidebar { width: 330px; background: #fff; border-right:1px solid #d1d9e6; display:flex; flex-direction:column; box-shadow: 2px 0 10px rgba(0,0,0,0.05); }
.sidebar-header { padding: 25px; background: linear-gradient(135deg, #0072bb 0%, #005a96 100%); color: white; }
.sidebar-header h2 { margin: 0; font-size: 1.3rem; }

.filters-container { padding: 15px; background: #fbfcfe; border-bottom: 1px solid #d1d9e6; }
.source-filters { display:flex; gap:8px; margin-bottom:12px; flex-wrap:wrap; }
.source-filters label { background: white; border: 1px solid #ced4da; padding: 5px 10px; border-radius: 20px; font-size: 0.8rem; cursor: pointer; transition: 0.2s; }
.source-filters label:hover { border-color: #0072bb; background: #f0f8ff; }
.search-box { width: 100%; padding: 10px; border-radius: 6px; border: 1px solid #ced4da; }

.category-list { overflow-y: auto; flex: 1; padding: 0; list-style: none; }
.category-item { padding: 12px 25px; border-bottom: 1px solid #edf1f7; cursor: pointer; display: flex; justify-content: space-between; transition: 0.2s; }
.category-item:hover { background: #f4f8fb; padding-left: 30px; }
.category-item .badge { background: #e9ecef; color: #495057; border-radius: 12px; }

/* Content */
.main-content { flex: 1; overflow-y: auto; padding: 40px; scroll-behavior: smooth; }
.category-title { color: #333; border-bottom: 2px solid #0072bb; padding-bottom: 5px; margin-bottom: 25px; }

.component-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
.component-card { background: white; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.04); border: 1px solid #d1d9e6; overflow: hidden; transition: 0.3s; }
.component-card:hover { transform: translateY(-3px); box-shadow: 0 8px 20px rgba(0,0,0,0.08); }

.card-header { padding: 10px 15px; background: #f8fafc; border-bottom: 1px solid #edf1f7; display: flex; justify-content: space-between; align-items: center; cursor: copy; font-family: monospace; color: #d63384; font-weight: bold; }
.card-body { padding: 15px; display: flex; justify-content: center; align-items: center; min-height: 110px; }

.source-badge { font-size: 0.6rem; padding: 2px 6px; border-radius: 4px; color: white; margin-left: 4px; font-family: sans-serif; text-transform: uppercase; }
.source-bootstrap { background: #6f42c1; }
.source-poncho { background: #0072bb; }
.source-íconos { background: #28a745; }

.update-badge { font-size: 0.8rem; margin-top: 5px; background: rgba(255,255,255,0.15); padding: 5px 10px; border-radius: 6px; display: inline-block; }
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
