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

Para sincronizar las clases, descargar los últimos archivos CSS y subir los cambios a GitHub de un solo golpe, ejecuta:

```bash
curl -L -o css/poncho.min.css https://cdn.jsdelivr.net/gh/argob/poncho@release-1.x/dist/css/poncho.min.css && curl -L -o css/icono-arg.css https://cdn.jsdelivr.net/gh/argob/poncho@release-1.x/dist/css/icono-arg.css && python3 generate_cheatsheet.py && git add . && git commit -m "Sincronización automática de clases" && git push origin main
```

Este comando:
1. Actualiza tus archivos locales en `/css` desde el repositorio oficial de Poncho (v1.x).
2. Extrae las nuevas clases (incluyendo iconos nuevos como **tableau**).
3. Regenera el buscador `index.html` y la base de datos `js/data.js`.
4. Sube todo a tu repositorio remoto.


*Nota:* Se recomienda conexión a internet para cargar las tipografías oficiales de Google Fonts.
