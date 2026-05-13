# Stage 1: フロントエンドのビルド
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

# Stage 2: Pythonバックエンド + フロントエンド静的ファイル
FROM python:3.11-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

EXPOSE 8080

CMD ["uvicorn", "src.api.server:app", "--host", "0.0.0.0", "--port", "8080"]
