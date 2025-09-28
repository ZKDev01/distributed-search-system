FROM python:3.11-slim

# Evitar archivos .pyc y hacer logging sin buffer
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DOCSEARCH_DB_PATH=/data/doc_search.db

WORKDIR /app

# Instalar dependencias
COPY doc-search-mvp/server/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la API
COPY doc-search-mvp/server/ /app/

# Crear usuario no root y directorio de datos
RUN useradd -m appuser \
    && mkdir -p /data \
    && chown -R appuser:appuser /data /app

USER appuser

VOLUME ["/data"]

EXPOSE 8000

# Healthcheck simple usando Python estándar
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0) if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2).getcode()==200 else sys.exit(1)"

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
