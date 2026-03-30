# Poncho Cheatsheet ARG

Una guía interactiva de clases y componentes de **Poncho** y **Bootstrap 3**, adaptada para el diseño oficial de Argentina.gob.ar.

## Descripción

Este repositorio contiene una herramienta visual para buscar y explorar clases de CSS utilizadas en el ecosistema **Poncho**. Permite filtrar clases por fuente (Bootstrap, Poncho, FontAwesome, Iconos ARG) y facilita la implementación de interfaces alineadas con el manual de diseño del Estado Argentino.

## Características

- 🌐 **Sincronización Automática de Clases:** El script extrae y clasifica las clases dinámicamente conectándose a las URLs oficiales de `Argentina.gob.ar`, garantizando una base de datos de clases siempre actualizada.
- 🖼️ **Aislamiento Visual Controlado:** Mientras que la recolección de clases se hace por red, el renderizado y preview de la aplicación web sigue leyendo tus archivos CSS alojados de forma local y segura en `css/`.
- ⏱️ **Timestamp de Generación:** Cada vez que generas la guía, se graba la fecha y hora actual en el panel lateral.
- ⚡ **Buscador rápido:** Filtrado instantáneo por categorías y fuentes.
- 🎨 **Estética moderna:** Diseño optimizado con micro-animaciones.

## Despliegue

El proyecto funciona en entornos estáticos como **Cloudflare Pages** o **GitHub Pages**, ofreciendo una versión rápida y accesible en la nube.

## 🔄 Cómo Actualizar (Sincronización Automática)

El proceso de extracción de clases ahora es **completamente automático**. Ya no necesitas descargar archivos para tener tu buscador al día. La herramienta se conecta y se sincroniza directamente con los repositorios web del Estado.

Para lanzar la actualización automática de la base de datos:

1. Ejecuta el archivo generador. Este comando descargará de Internet los últimos archivos `.css` de Poncho y Bootstrap 3, extraerá las clases y regenerará la base interna `js/data.js` al instante.
   ```bash
   python3 generate_cheatsheet.py
   ```
2. *(Opcional)* El frontend de la página web (la gráfica que tú ves) sí seguirá usando los archivos seguros y controlados de tu carpeta `/css`. Solo si ocurre un cambio de diseño gigante de parte de Presidencia que necesites ver en tu preview local, puedes optar por bajarlos físicamente a la carpeta `css/`.
3. Sube la actualización automática de las clases a tu repositorio:
   ```bash
   git add .
   git commit -m "Sincronización automática de clases desde fuente oficial"
   git push origin main
   ```

*Nota:* Se recomienda conexión a internet para cargar las tipografías oficiales de Google Fonts.
