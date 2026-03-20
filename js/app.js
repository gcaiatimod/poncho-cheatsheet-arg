
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

// Petición para verificar actualizaciones
if (window.location.protocol.startsWith('http')) {
    fetch('php/check_updates.php')
        .then(res => {
            if (!res.ok) throw new Error('PHP no disponible');
            return res.json();
        })
        .then(data => {
            const badge = document.getElementById('updateBadge');
            if(badge.querySelector('.dot')) {
                badge.querySelector('.dot').style.animation = 'none';
                badge.querySelector('.dot').style.display = 'none';
            }
            
            if (data.up_to_date) {
                badge.innerHTML = `✓ Actualizado (Servidor: ${data.last_modified})`;
                badge.classList.add('success');
            } else {
                badge.innerHTML = `⚠️ ¡Hay una versión online nueva! (Servidor: ${data.last_modified})`;
                badge.classList.add('warning');
            }
        })
        .catch(err => {
            // Si el PHP falla (ej: en GitHub Pages), simplemente ocultamos el badge
            const badge = document.getElementById('updateBadge');
            if (badge) badge.style.display = 'none';
            console.log("Verificación de actualizaciones deshabilitada (Entorno estático o PHP no configurado).");
        });
} else {
    const badge = document.getElementById('updateBadge');
    if (badge) badge.style.display = 'none';
}
