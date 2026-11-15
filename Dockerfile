FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd --create-home appuser && mkdir -p /app/.runtime && chown -R appuser:appuser /app
USER appuser
EXPOSE 8501
CMD ["python", "-m", "streamlit", "run", "capstone/app.py", "--server.address", "0.0.0.0", "--server.port", "8501", "--server.headless", "true"]
