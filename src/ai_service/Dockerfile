FROM python:3.11-slim
WORKDIR /app
COPY src/ai_service/requirements-ai.txt /tmp/requirements-ai.txt
# Install curl for healthchecks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r /tmp/requirements-ai.txt
COPY src/ai_service /app
ENV PYTHONPATH=/app
RUN useradd -m appuser || true
USER appuser
EXPOSE 9000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000"]
