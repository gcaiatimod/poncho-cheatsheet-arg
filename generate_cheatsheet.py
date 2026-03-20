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
    <title>Poncho Cheatsheet ARG - Local</title>
    <link rel="stylesheet" href="css/bootstrap.min.css">
    <link rel="stylesheet" href="css/icono-arg.css">
    <link rel="stylesheet" href="css/poncho.min.css">
    <link rel="stylesheet" href="css/style.css">
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
                    <label><input type="checkbox" value="Bootstrap" checked> Bootstrap 3</label>
                    <label><input type="checkbox" value="Poncho" checked> Poncho</label>
                    <label><input type="checkbox" value="Íconos" checked> Íconos ARG</label>
                </div>
                <input type="text" id="searchInput" class="search-box" placeholder="Buscar clase...">
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
    if (category === 'Íconos ARG') return `<div style="text-align:center"><i class="${cls}" style="font-size: 2rem; color: #0072bb;"></i><br><br><small>.${cls}</small></div>`;
    if (category === 'Botones') return `<button type="button" class="btn ${cls}">Botón ${cls}</button>`;
    if (category === 'Alertas') return `<div class="alert ${cls}" style="width:100%">Alerta: ${cls}</div>`;
    if (category === 'Insignias/Etiquetas') return `<span class="${cls}">${cls}</span>`;
    return `<div class="${cls}" style="padding: 10px; border: 1px dashed #ccc; display: inline-block;">.${cls}</div>`;
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
                    <div>${drawSourceBadges(item.sources)}</div>
                </div>
                <div class="card-body">${generateHTMLForClass(item.name, catName)}</div>
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
body { font-family: sans-serif; background: #f4f6f9; margin:0; }
.cheatsheet-container { display: flex; height: 100vh; overflow: hidden; }
.sidebar { width: 320px; background: #fff; border-right: 1px solid #ddd; display: flex; flex-direction: column; }
.sidebar-header { padding: 20px; background: #0072bb; color: white; }
.filters-container { padding: 15px; background: #f9f9f9; border-bottom: 1px solid #ddd; }
.source-filters { display: flex; gap: 10px; margin-bottom:10px; flex-wrap: wrap; }
.search-box { width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; }
.category-list { overflow-y: auto; flex: 1; margin: 0; padding: 0; list-style: none; }
.category-item { padding: 12px 20px; border-bottom: 1px solid #eee; cursor: pointer; display: flex; justify-content: space-between; }
.category-item:hover { background: #f0f8ff; }
.main-content { flex: 1; overflow-y: auto; padding: 30px; }
.category-title { border-bottom: 2px solid #0072bb; padding-bottom: 10px; margin-bottom: 20px; }
.component-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 15px; }
.component-card { background: white; border-radius: 6px; border: 1px solid #ddd; overflow: hidden; }
.card-header { padding: 10px; background: #f1f1f1; display: flex; justify-content: space-between; cursor: pointer; font-family: monospace; }
.card-body { padding: 15px; display: flex; justify-content: center; align-items: center; min-height: 100px; }
.source-badge { font-size: 0.6rem; padding: 2px 5px; border-radius: 3px; color: white; margin-left: 3px; }
.source-bootstrap { background: #563d7c; }
.source-poncho { background: #0072bb; }
.source-íconos { background: #28a745; }
.update-badge { font-size: 0.8rem; margin-top: 5px; opacity: 0.8; }
"""

# Categorización y guardado
categorized_filtered = {k: v for k, v in categorized.items() if len(v) > 0}
json_data = json.dumps(categorized_filtered)
timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")

html_content = html_template.replace('{TIMESTAMP_PLACEHOLDER}', timestamp)
with open('js/data.js', 'w', encoding='utf-8') as f: f.write('const categorizedData = ' + json_data + ';')
with open('js/app.js', 'w', encoding='utf-8') as f: f.write(js_template)
with open('css/style.css', 'w', encoding='utf-8') as f: f.write(css_template)
with open('index.html', 'w', encoding='utf-8') as f: f.write(html_content)

print('✅ index.html generado con éxito (Sin errores).')
