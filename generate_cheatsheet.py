import re
import json
import os
import time
import urllib.request
from datetime import datetime

# --- MODO MANUAL: Usa archivos locales en la carpeta css/ ---
def parse_css(path_or_url):
    if path_or_url.startswith('http'):
        with urllib.request.urlopen(path_or_url) as response:
            content = response.read().decode('utf-8', errors='ignore')
    else:
        with open(path_or_url, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    
    # Remove comments
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    
    # Find all classes
    classes = set()
    for match in re.finditer(r'\.([a-zA-Z0-9_-]+)', content):
        classes.add(match.group(1))
    
    return classes

bs_classes = parse_css('css/bootstrap.min.css')
poncho_classes = parse_css('css/poncho.min.css')
icono_classes = parse_css('css/icono-arg.css')
fa_classes = parse_css('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css')

all_classes = bs_classes.union(poncho_classes).union(icono_classes).union(fa_classes)

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
    'Íconos FA': r'^fa-.*$',
    'Poncho Específicos': r'^(p-.*|border-.*|rounded-.*|shadow-.*|w-\d+|h-\d+|d-.*|align-.*|justify-.*)$'
}

categorized = {cat: [] for cat in categories}

for cls in all_classes:
    sources = []
    if cls in bs_classes: sources.append('Bootstrap')
    if cls in poncho_classes: sources.append('Poncho')
    if cls in icono_classes: sources.append('Íconos')
    if cls in fa_classes: sources.append('FontAwesome')
    
    matched = False
    for cat, regex in categories.items():
        if re.match(regex, cls):
            categorized[cat].append({"name": cls, "sources": sources})
            matched = True
            break

html_template = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Poncho Cheatsheet ARG - Bootstrap 3 & Poncho (Argentina.gob.ar)</title>
    <!-- CSS Locales -->
    <link rel="stylesheet" href="css/bootstrap.min.css">
    <link rel="stylesheet" href="css/icono-arg.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    <link rel="stylesheet" href="css/poncho.min.css">
    <link rel="stylesheet" href="css/style.css">
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
                    <label><input type="checkbox" value="FontAwesome" checked> FontAwesome</label>
                </div>
                <input type="text" id="searchInput" class="search-box" placeholder="Buscar clase (ej: primary)...">
            </div>
            <ul class="category-list" id="categoryList">
                <!-- Nodos insertados via JS -->
            </ul>
        </aside>
        
        <main class="main-content" id="mainContent">
            <!-- Nodos insertados via JS -->
        </main>
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
    const isHidden = cls.includes('hidden') || cls.includes('sr-only') || cls.includes('d-none');
    
    if (category === 'Íconos ARG') {
        return `<div style="text-align:center"><i class="${cls} icono-preview"></i><br><br><small style="color: #666;">&lt;i class="${cls}"&gt;&lt;/i&gt;</small></div>`;
    } else if (category === 'Íconos FA') {
        const isModifier = /^fa-(lg|[2-5]x|fw|li|ul|border|pull-.*|spin|pulse)$/.test(cls);
        if (isModifier) {
            return `<div style="text-align:center; color: #666;">
                        <div style="margin-bottom:10px;"><i class="fa fa-flag ${cls}"></i></div>
                        <small>&lt;i class="fa fa-flag ${cls}"&gt;&lt;/i&gt;</small>
                        <div style="font-size: 0.75rem; margin-top:5px; color:#999;">(Clase de utilidad/tamaño)</div>
                    </div>`;
        }
        return `<div style="text-align:center"><i class="fa ${cls} icono-preview"></i><br><br><small style="color: #666;">&lt;i class="fa ${cls}"&gt;&lt;/i&gt;</small></div>`;
    } else if (category === 'Botones') {
        return `<button type="button" class="btn ${cls}">Botón ${cls}</button>`;
    } else if (category === 'Alertas') {
        return `<div class="alert ${cls}" style="width:100%">Ejemplo de Alerta: ${cls}</div>`;
    } else if (category === 'Paneles') {
        return `<div class="panel ${cls}" style="width:100%"><div class="panel-heading">Encabezado</div><div class="panel-body">Cuerpo del panel</div></div>`;
    } else if (category === 'Tipografía') {
        return `<p class="${cls}">Ejemplo de texto con ${cls}</p>`;
    } else if (category === 'Insignias/Etiquetas') {
        return `<span>Ejemplo: </span><span class="${cls}">${cls}</span>`;
    } else if (category === 'Tablas') {
        return `<table class="table ${cls}" style="width:100%"><tr><td>Ejemplo Celda</td></tr></table>`;
    } else if (category === 'Grup. Listas') {
        return `<ul class="list-group ${cls}" style="width:100%"><li class="list-group-item">Lista Ítem</li></ul>`;
    } else if (isHidden) {
        return `<div style="width:100%; text-align:center"><div class="${cls}">Este texto está oculto por la clase ${cls}</div><div style="color: #999; font-size: 0.8em; margin-top: 10px;">(El elemento se encuentra oculto a propósito)</div></div>`;
    } else {
        return `<div class="${cls}" style="padding: 10px; background: rgba(0,0,0,0.05); border: 1px dashed #ccc; display: inline-block;">.${cls}</div>`;
    }
}

function drawSourceBadges(sources) {
    return sources.map(s => {
        if (s === 'Bootstrap') return '<span class="source-badge badge-bs" title="Viene de Bootstrap">BS3</span>';
        if (s === 'Poncho') return '<span class="source-badge badge-po" title="Viene de Poncho">Poncho</span>';
        if (s === 'Íconos') return '<span class="source-badge badge-ic" title="Viene de Iconos">Íconos</span>';
        if (s === 'FontAwesome') return '<span class="source-badge badge-fa" title="Viene de FontAwesome">FA</span>';
        return '';
    }).join('');
}

function render() {
    const filterText = searchInput.value.trim().toLowerCase();
    const activeSources = Array.from(sourceCheckboxes)
                               .filter(cb => cb.checked)
                               .map(cb => cb.value);

    categoryList.innerHTML = '';
    mainContent.innerHTML = '';
    
    let totalCards = 0;

    for (const [catName, items] of Object.entries(categorizedData)) {
        // Filter items based on source and then search text
        const filteredItems = items.filter(item => {
            const sourceMatch = item.sources.some(s => activeSources.includes(s));
            if (!sourceMatch) return false;
            
            const htmlContent = generateHTMLForClass(item.name, catName).toLowerCase();
            const textMatch = item.name.toLowerCase().includes(filterText) || 
                              catName.toLowerCase().includes(filterText) || 
                              htmlContent.includes(filterText);
            return textMatch;
        });
        
        if (filteredItems.length === 0) continue;
        
        totalCards += filteredItems.length;

        // Sort items by name alphabetically
        filteredItems.sort((a,b) => a.name.localeCompare(b.name));

        // Build Sidebar item
        const li = document.createElement('li');
        li.className = 'category-item';
        li.innerHTML = `<span>${catName}</span> <span class="badge">${filteredItems.length}</span>`;
        li.onclick = () => {
            document.getElementById('cat-' + catName).scrollIntoView({ behavior: 'smooth', block: 'start' });
            document.querySelectorAll('.category-item').forEach(el => el.classList.remove('active'));
            li.classList.add('active');
        };
        categoryList.appendChild(li);

        // Build Main Section
        const section = document.createElement('section');
        section.className = 'category-section';
        section.id = 'cat-' + catName;
        
        const h3 = document.createElement('h3');
        h3.className = 'category-title';
        h3.innerText = `${catName} (${filteredItems.length} clases)`;
        section.appendChild(h3);
        
        const grid = document.createElement('div');
        grid.className = 'component-grid';
        
        filteredItems.forEach(item => {
            const cls = item.name;
            const card = document.createElement('div');
            card.className = 'component-card';
            
            const header = document.createElement('div');
            header.className = 'card-header';
            header.title = 'Clic para copiar el nombre de la clase';
            header.setAttribute('aria-label', `Clase CSS: ${cls}. Clic o Enter para copiar al portapapeles.`);
            header.tabIndex = 0;
            header.style.cursor = 'copy';
            header.innerHTML = `<span>.${cls}</span> <div style="display:flex;">${drawSourceBadges(item.sources)}</div>`;
            
            const handleCopy = async () => {
                try {
                    await navigator.clipboard.writeText(cls);
                    const span = header.querySelector('span');
                    const originalText = span.innerText;
                    span.innerText = '¡Copiado! ✓';
                    span.style.color = '#28a745';
                    
                    setTimeout(() => {
                        span.innerText = originalText;
                        span.style.color = '';
                    }, 1200);
                } catch (err) {
                    console.error('No se pudo copiar: ', err);
                }
            };

            header.addEventListener('click', handleCopy);
            header.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') handleCopy();
            });
            
            const body = document.createElement('div');
            body.className = 'card-body';
            body.innerHTML = generateHTMLForClass(cls, catName);
            
            card.appendChild(header);
            card.appendChild(body);
            grid.appendChild(card);
        });
        
        section.appendChild(grid);
        mainContent.appendChild(section);
    }
    
    if (totalCards === 0) {
        mainContent.innerHTML = '<div class="no-results"><h2>No se encontraron resultados combinando esos filtros</h2><p>Intenta marcando otras opciones o cambiando el texto de búsqueda.</p></div>';
    }
}

// Initialize
render();

// Listeners for inputs
searchInput.addEventListener('input', render);
sourceCheckboxes.forEach(cb => cb.addEventListener('change', render));

// Verificación de actualizaciones deshabilitada (Se gestiona vía GitHub Actions)
console.log("Poncho Cheatsheet ARG: Listo.");
"""

css_template = """
body { font-family: 'Encode Sans', sans-serif, Arial; background-color: #f8f9fa; margin: 0; padding: 0; }
.cheatsheet-container { display: flex; height: 100vh; overflow: hidden; }

/* Sidebar */
.sidebar { width: 330px; background: #fff; border-right: 1px solid #e0e0e0; display: flex; flex-direction: column; }
.sidebar-header { padding: 20px; border-bottom: 1px solid #e0e0e0; background: #0072bb; color: white;}
.sidebar-header h2 { margin: 0; font-size: 1.2rem; font-weight: bold; }

.filters-container { padding: 15px; border-bottom: 1px solid #e0e0e0; background: #f9f9f9; }
.source-filters { display: flex; gap: 10px; margin-bottom: 15px; flex-wrap: wrap; }
.source-filters label { cursor: pointer; font-size: 0.9rem; display: flex; align-items: center; gap: 5px; background: white; padding: 6px 10px; border-radius: 4px; border: 1px solid #dee2e6; user-select: none; transition: background 0.2s, border-color 0.2s; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
.source-filters label:hover { background: #f0f8ff; border-color: #0072bb; }
.source-filters input[type="checkbox"] { margin: 0; cursor: pointer; width: 16px; height: 16px; accent-color: #0072bb; }

.search-box { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }

.category-list { overflow-y: auto; flex: 1; padding: 0; margin: 0; list-style: none; }
.category-item { padding: 10px 20px; border-bottom: 1px solid #f0f0f0; cursor: pointer; transition: background 0.2s; display: flex; justify-content: space-between; align-items: center;}
.category-item:hover { background: #f0f8ff; }
.category-item.active { background: #0072bb; color: white; border-right: 4px solid #005a96; }
.category-item .badge { background: rgba(0,0,0,0.1); padding: 2px 6px; border-radius: 10px; font-size: 0.8rem; }
.category-item.active .badge { background: rgba(255,255,255,0.2); }

/* Main Content */
.main-content { flex: 1; overflow-y: auto; padding: 20px 40px; background: #f8f9fa; scroll-behavior: smooth; }

.category-section { margin-bottom: 60px; }
.category-title { border-bottom: 2px solid #0072bb; padding-bottom: 10px; margin-bottom: 20px; color: #333; }

.component-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
.component-card { background: white; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); border: 1px solid #e0e0e0; overflow: hidden; transition: box-shadow 0.2s; transform: translateZ(0); min-height: 120px; display: flex; flex-direction: column; }
.component-card:hover { box-shadow: 0 5px 15px rgba(0,0,0,0.1); }

.card-header { padding: 10px 15px; background: #f1f1f1; border-bottom: 1px solid #e0e0e0; font-family: monospace; font-size: 0.9rem; color: #d63384; font-weight: bold; display: flex; justify-content: space-between; align-items: center; }
.source-badge { font-family: sans-serif; font-size: 0.65rem; color: white; padding: 2px 5px; border-radius: 4px; font-weight: bold; text-transform: uppercase; margin-left: 5px; }
.badge-bs { background: #563d7c; }
.badge-po { background: #0072bb; }
.badge-ic { background: #28a745; }
.badge-fa { background: #17a2b8; }

.card-body { padding: 15px; overflow-x: auto; position: relative; flex: 1; display:flex; align-items:center; justify-content:center; }

.icono-preview { font-size: 2rem; color: #0072bb; }

.no-results { text-align: center; color: #666; padding: 40px; }

/* Update Badge */
.update-badge { margin-top: 10px; font-size: 0.8rem; padding: 5px 8px; border-radius: 4px; display: inline-flex; align-items: center; gap: 5px; background: rgba(255,255,255,0.15); color: #fff; border: 1px solid rgba(255,255,255,0.3); }
.update-badge.success { background: #28a745; border-color: #218838; }
.update-badge.warning { background: #ffc107; color: #333; border-color: #e0a800; }
.update-badge .dot { width: 8px; height: 8px; border-radius: 50%; background: #fff; animation: pulse 1.5s infinite; }
@keyframes pulse { 0% { opacity: 0.5; } 50% { opacity: 1; } 100% { opacity: 0.5; } }
"""

categorized_filtered = {k: v for k, v in categorized.items() if len(v) > 0}
json_data = json.dumps(categorized_filtered)

timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
html_content = html_template.replace('{TIMESTAMP_PLACEHOLDER}', timestamp)
html_content = html_content.replace('js/data.js', f'js/data.js?v={int(time.time())}').replace('js/app.js', f'js/app.js?v={int(time.time())}')

with open('js/data.js', 'w', encoding='utf-8') as f:
    f.write('const categorizedData = ' + json_data + ';')

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(js_template)

with open('css/style.css', 'w', encoding='utf-8') as f:
    f.write(css_template)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print('Generated index.html successfully with source filters.')
