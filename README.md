# Poncho Cheatsheet ARG

Una guía interactiva de clases y componentes de **Poncho** y **Bootstrap 3**, adaptada para el diseño oficial de Argentina.gob.ar.

## Descripción

Este repositorio contiene una herramienta visual para buscar y explorar clases de CSS utilizadas en el ecosistema **Poncho**. Permite filtrar clases por fuente (Bootstrap, Poncho, FontAwesome, Iconos ARG) y facilita la implementación de interfaces alineadas con el manual de diseño del Estado Argentino.

## Características

- 🛠️ **Actualización Manual:** Tú controlas cuándo se actualizan los archivos CSS.
- ⏱️ **Timestamp de Generación:** Cada vez que generas la guía, se graba la fecha y hora actual en el panel lateral.
- ⚡ **Buscador rápido:** Filtrado instantáneo por categorías y fuentes.
- 🎨 **Estética moderna:** Diseño optimizado con micro-animaciones y glassmorphism.

## Despliegue

El proyecto funciona en entornos estáticos como **Cloudflare Pages** o **GitHub Pages**, ofreciendo una versión rápida y accesible en la nube.

## Cómo Actualizar

Para actualizar la guía con nuevos estilos CSS:
1. Descarga los nuevos archivos `.css` oficiales y pégalos en la carpeta `css/`.
2. Ejecuta el script de generación:
   ```bash
   python3 generate_cheatsheet.py
   ```
3. Sube los cambios a GitHub:
   ```bash
   git add .
   git commit -m "Actualización manual de estilos"
   git push origin main
   ```

*Nota:* Se recomienda conexión a internet para cargar las tipografías oficiales de Google Fonts.
