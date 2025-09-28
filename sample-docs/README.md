# sample-docs

Este directorio contiene archivos de ejemplo para probar la app:

- `manual_de_usuario.txt`
- `reporte_financiero_2024.csv`
- `propuesta_proyecto.md`

Puedes usarlos así:

1) Arranca el servidor FastAPI.
2) Abre la app de Streamlit.
3) En la pestaña "Gestión de Archivos", haz upsert de metadatos usando las rutas de estos archivos, por ejemplo:

```text
file_id: f_manual
name: manual_de_usuario.txt
path: E:\\Universidad\\4to Año\\SD\\Proyecto\\distributed-search-system\\sample-docs\\manual_de_usuario.txt
mime_type: text/plain
size: 0 (o el tamaño real si lo conoces)
```

Luego busca por términos como "manual", "reporte" o "propuesta" en la pestaña "Búsqueda".

Nota: estos archivos no se indexan automáticamente; la app guarda metadatos en SQLite y la búsqueda es por nombre.
