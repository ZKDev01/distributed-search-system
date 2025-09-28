FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SERVER_URL=http://api:8000

WORKDIR /app

COPY doc-search-mvp/client/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY doc-search-mvp/client/ /app/

EXPOSE 8501

# Usar un usuario no root
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

CMD ["streamlit", "run", "streamlit_app.py", "--server.address", "0.0.0.0", "--server.port", "8501"]
