# distributed-search-system

MVP de un sistema de búsqueda de documentos con FastAPI (server) y un cliente CLI mínimo.

Estructura principal:

- `doc-search-mvp/server/`: API FastAPI + SQLite
- `doc-search-mvp/client/`: CLI simple (requests)
- `tests/`: pruebas E2E (pytest) y script de seed


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


## 2) Cliente CLI (opcional)

El cliente CLI permite hacer una llamada básica al endpoint de salud.

```powershell
python -m venv .venv-client
.\.venv-client\Scripts\Activate.ps1
pip install -r .\doc-search-mvp\client\requirements.txt
python .\doc-search-mvp\client\cli.py health
# O apuntando a otra URL:
python .\doc-search-mvp\client\cli.py --server http://localhost:8000 health
```


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


## Notas y consideraciones

- Base de datos: se usa SQLite en un archivo junto a `db.py` (por defecto `doc_search.db`).
- Búsqueda por nombre: si SQLite tiene FTS5, se usa una tabla virtual `fts_name` para búsquedas rápidas; si no, se hace fallback a `LIKE`.
- Seguridad y producción: este MVP está orientado a desarrollo. Para producción, se recomienda revisar configuración de procesos (workers), logging, seguridad (usuario no root en imagen Docker), y persistencia de la base de datos en un volumen dedicado.
- Rutas Windows: cuando envíes `path` en JSON, recuerda escapar correctamente las barras (por ejemplo `C:\\ruta\\archivo.txt`).


## Problemas comunes

- Importaciones no resueltas en el editor (fastapi, pydantic, uvicorn): instala las dependencias del servidor en tu entorno virtual.
- Puerto ocupado: cambia el puerto al arrancar Uvicorn manualmente o detén el proceso que lo usa.
- FTS5 no disponible: las búsquedas seguirán funcionando con `LIKE`, aunque con menor performance.
