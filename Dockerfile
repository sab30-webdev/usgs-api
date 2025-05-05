FROM python:3.12.10-slim

WORKDIR /app

COPY requirements.txt .

# Install dependencies and clean up the cache to reduce image size
RUN pip install --no-cache-dir -r requirements.txt && rm -rf /root/.cache

COPY . .

EXPOSE 8000

# Run the FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
