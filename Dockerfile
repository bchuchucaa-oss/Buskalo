
# Imagen oficial de Python
FROM python:3.13-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Evitar archivos .pyc y mostrar logs inmediatamente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar configuración y código del proyecto
COPY alembic.ini .
COPY alembic ./alembic
COPY src ./src

# Puerto de FastAPI
EXPOSE 8000

# Iniciar la aplicación
CMD ["python", "-m", "uvicorn", "near_market.main:app", "--host", "0.0.0.0", "--port", "8000"]
