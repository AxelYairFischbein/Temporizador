FROM python:3.11-slim

# Instalar dependencias del sistema para tkinter y pynput
RUN apt-get update && apt-get install -y \
    python3-tk \
    xauth \
    x11-apps \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements y instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el script
COPY temporizador.py .

# Permitir acceso a X11 (necesario para GUI)
ENV DISPLAY=:0

# Ejecutar la aplicación
CMD ["python", "temporizador.py"]
