
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
