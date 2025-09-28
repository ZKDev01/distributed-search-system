# distributed-search-system

MVP de un sistema de búsqueda de documentos con FastAPI (server) y un cliente en Streamlit (UI web local).

Estructura principal:

- `doc-search-mvp/server/`: API FastAPI + SQLite
- `doc-search-mvp/client/`: App Streamlit (UI) que consume la API
- `tests/`: pruebas E2E (pytest) y script de seed
- `sample-docs/`: archivos de ejemplo para pruebas locales con la UI (no se suben al repo, salvo su README)


## Requisitos

- Python 3.11+ (recomendado)
- PowerShell (estas instrucciones usan PowerShell en Windows)
- Opcional: Docker


## 1) Instalar y arrancar el servidor

En una terminal PowerShell desde la raíz del repo:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r .\doc-search-mvp\server\requirements.txt
python .\doc-search-mvp\server\main.py
```

El servidor expone por defecto:

- Salud: <http://localhost:8000/health>
- Endpoints principales:
  - POST `/files` (upsert de metadatos de archivo)
  - DELETE `/files/{file_id}`
  - GET `/search?q=texto&limit=20`


### Probar rápidamente con PowerShell

Health:

```powershell
Invoke-RestMethod -Method GET http://localhost:8000/health
```

Upsert de un archivo (ejemplo):

```powershell
$body = @{
  file_id = "f1"; name = "manual.txt"; path = "C:\\docs\\manual.txt";
  mime_type = "text/plain"; size = 1234; last_modified = 1699999999; indexed_at = 1699999999
} | ConvertTo-Json
Invoke-RestMethod -Method POST http://localhost:8000/files -ContentType 'application/json' -Body $body
```

Buscar por nombre:

```powershell
Invoke-RestMethod -Method GET "http://localhost:8000/search?q=manual&limit=10"
```

Eliminar:

```powershell
Invoke-RestMethod -Method DELETE http://localhost:8000/files/f1
```

## 2) Cliente Streamlit (UI web)

La app de Streamlit proporciona una interfaz para:

- Verificar el estado del servidor.
- Buscar documentos por nombre.
- Hacer upsert (crear/actualizar) de metadatos de archivos.
- Eliminar un archivo por `file_id`.

Requisitos del cliente (se instalan desde `doc-search-mvp/client/requirements.txt`):

- streamlit
- requests
- python-dotenv (opcional)

Puedes usar el mismo entorno virtual del servidor o crear uno separado. Ejemplos con PowerShell en Windows:

Opción A: Reusar el entorno del servidor (ya activado en el paso 1)

```powershell
# Con el venv del servidor ya activo
pip install -r .\doc-search-mvp\client\requirements.txt
streamlit run .\doc-search-mvp\client\streamlit_app.py
```

Opción B: Crear un entorno separado para el cliente

```powershell
python -m venv .venv-client
.\.venv-client\Scripts\Activate.ps1
pip install -r .\doc-search-mvp\client\requirements.txt
streamlit run .\doc-search-mvp\client\streamlit_app.py
```

Por defecto Streamlit abrirá <http://localhost:8501>. En la barra lateral puedes configurar la URL del servidor (por defecto `http://localhost:8000`). Asegúrate de que el servidor FastAPI esté corriendo antes de usar la UI.

### Qué puedes hacer desde la UI

- Salud: la barra lateral muestra si el servidor responde en `/health`.
- Búsqueda: en la pestaña “Búsqueda”, ingresa texto y define el límite para consultar `GET /search`.
- Gestión de Archivos: en la pestaña homónima puedes:
  - Upsert (POST `/files`): envía `file_id`, `name`, `path` y opcionalmente `mime_type`, `size`, `last_modified`, `indexed_at` (la UI rellena `last_modified` e `indexed_at` con la hora actual al guardar).
  - Eliminar (DELETE `/files/{file_id}`): escribe el `file_id` y pulsa “Eliminar”.

Notas:

- La UI no sube ni lee contenido de archivos; sólo gestiona metadatos guardados en SQLite.
- Las rutas Windows en JSON deben ir con barras escapadas (por ejemplo: `C:\\ruta\\archivo.txt`).


## 3) Pruebas E2E con pytest

Las pruebas usan FastAPI TestClient y una base de datos SQLite temporal por test (no afecta tu DB local).

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r .\tests\requirements.txt
pytest -q
```

Incluye casos para `/health`, flujo upsert → search → delete, etc.


## 4) Script de seed (smoke test manual)

Con el servidor corriendo en `http://127.0.0.1:8000`:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r .\tests\requirements.txt
python .\tests\seed.py
```

Inserta un par de archivos de ejemplo y luego ejecuta una búsqueda. Imprime en consola lo insertado y los resultados.


## 5) Docker (opcional)

Construir y correr el servidor en Docker:

```powershell
docker build -t doc-search-mvp-server -f .\doc-search-mvp\server\Dockerfile .
docker run -p 8000:8000 doc-search-mvp-server
```

### Docker Compose (API + UI) – despliegue local no distribuido

Para levantar la API (FastAPI + SQLite) y la UI (Streamlit) juntas:

```powershell
docker compose build
docker compose up
```

Esto levantará:

- API en <http://localhost:8000> (con la base de datos persistida en un volumen `docsearch_data`).
- UI en <http://localhost:8501> apuntando a la API interna `<http://api:8000>` (configurable vía `SERVER_URL`).

Variables y volúmenes clave:

- `DOCSEARCH_DB_PATH=/data/doc_search.db` en el contenedor de la API.
- Volumen `docsearch_data` mapeado a `/data` para persistencia.

Para detener:

```powershell
docker compose down
```

Para limpiar el volumen de datos (¡esto borra la DB!):

```powershell
docker compose down -v
```


## Notas y consideraciones

- Base de datos: se usa SQLite en un archivo junto a `db.py` (por defecto `doc_search.db`).
- Búsqueda por nombre: si SQLite tiene FTS5, se usa una tabla virtual `fts_name` para búsquedas rápidas; si no, se hace fallback a `LIKE`.
- Seguridad y producción: este MVP está orientado a desarrollo. Para producción, se recomienda revisar configuración de procesos (workers), logging, seguridad (usuario no root en imagen Docker), y persistencia de la base de datos en un volumen dedicado.
- Rutas Windows: cuando envíes `path` en JSON, recuerda escapar correctamente las barras (por ejemplo `C:\\ruta\\archivo.txt`).

### Consideraciones específicas del cliente Streamlit

- La app Streamlit ejecuta las llamadas HTTP desde el proceso local de Streamlit (no desde el navegador), por lo que no hay problemas de CORS con FastAPI.
- Campos opcionales: en la UI, el campo `size` es numérico y su valor por defecto es `0`. Si no quieres guardar `size`, deja `0` y se enviará como `null` (None). Si necesitas guardar realmente tamaño `0`, la UI actual lo convertirá a `null`. Puedes ajustar el comportamiento cambiando la lógica en `streamlit_app.py` para enviar `0` explícito cuando aplique.
- Si `delete_id` está vacío y presionas “Eliminar”, la petición fallará (endpoint inválido). Asegúrate de completar el `file_id`.

#### Archivos de prueba (sample-docs)

En `sample-docs/` hay archivos de ejemplo (no se versionan) para probar los flujos con la UI. Carga sus metadatos desde la pestaña “Gestión de Archivos” y luego busca por términos como “manual”, “reporte” o “propuesta”.


## Problemas comunes

- Importaciones no resueltas en el editor (fastapi, pydantic, uvicorn): instala las dependencias del servidor en tu entorno virtual.
- Puerto ocupado: cambia el puerto al arrancar Uvicorn manualmente o detén el proceso que lo usa.
- FTS5 no disponible: las búsquedas seguirán funcionando con `LIKE`, aunque con menor performance.
- Streamlit no abre el navegador: revisa la salida de la terminal; accede manualmente a <http://localhost:8501>.
- “Servidor no disponible” en la barra lateral: verifica que FastAPI esté corriendo y que la URL del servidor sea correcta (http y puerto).
- Conflicto de puertos de Streamlit: si el 8501 está ocupado, puedes lanzar con `--server.port 8502`.

```powershell
streamlit run .\doc-search-mvp\client\streamlit_app.py --server.port 8502
```

---

Sugerencias futuras (no incluidas por defecto):

- Mejorar la UI para permitir dejar `size` en blanco en lugar de `0` y prevenir clicks de “Eliminar” con `file_id` vacío.
- Añadir validaciones mínimas en cliente (por ejemplo, impedir búsquedas vacías para evitar llamadas innecesarias).
