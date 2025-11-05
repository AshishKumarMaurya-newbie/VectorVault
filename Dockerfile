FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- CHANGED: Copy the whole project, not just 'src' ---
COPY . .

EXPOSE 8000

# --- CHANGED: The default command now cds into src first ---
CMD ["sh", "-c", "cd src && uvicorn main:app --host 0.0.0.0 --port 8000"]