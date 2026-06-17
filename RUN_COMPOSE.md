# RUN_COMPOSE

Prerequisites: Docker Desktop or Docker Engine with Compose v2.

1. Copy `.env.example` to `.env` and set values (do NOT commit `.env`).

Bash / WSL:
```
cp .env.example .env
```

PowerShell:
```
Copy-Item .env.example .env
```

2. Build and start the stack:

```
make compose-up
```

If `make` is not available on Windows, use:

```
docker compose up -d --build
```

3. Check health endpoints:

```
curl http://localhost:8000/health
curl http://localhost:9000/health
docker exec -it <db_container> pg_isready -U ${POSTGRES_USER}
```

PowerShell example:

```
Invoke-RestMethod http://localhost:8000/health
Invoke-RestMethod http://localhost:9000/health
```
4. Run Postman/Newman tests against `http://localhost:8000`.

5. Stop and remove the stack:

```
make compose-down
```
# RUN_COMPOSE.md – Hướng dẫn chạy Lab 05

Tài liệu này hướng dẫn người khác clone repo sạch và chạy lại stack Compose của Lab 05.

---

## 1. Clone repo

```bash
git clone <repo-url>
cd FIT4110_lab05_docker_compose_readiness
```

---

## 2. Cài dependencies cho Newman/Prism/Spectral (tuỳ chọn)

```bash
npm install
```

---

## 3. Build & chạy stack Docker Compose

```bash
# Copy .env.example sang .env và chỉnh sửa nếu cần
cp .env.example .env

# Build images (nếu chưa có) và khởi động các container trong nền
docker compose up -d --build
```

Lệnh trên sẽ tạo các container:

- `fit4110-db-lab05` (PostgreSQL)
- `fit4110-ai-lab05` (AI service mẫu chạy port 9000)
- `fit4110-api-lab05` (API FastAPI trên port 8000)

Theo dõi log:

```bash
docker compose logs -f
```

Sau vài giây, kiểm tra health của mỗi service:

```bash
# API
curl http://localhost:8000/health

# AI service
curl http://localhost:9000/health

# DB readiness
docker exec -it fit4110-db-lab05 pg_isready -U $POSTGRES_USER
```

Bạn cũng có thể truy cập endpoint `/predict` của AI service để xem kết quả mẫu:

```bash
curl -X POST http://localhost:9000/predict
```

---

## 4. Chạy Newman test trên stack Compose (tuỳ chọn)

```bash
npm run test:compose
```

Report sinh tại:

```text
reports/newman-lab05-compose.xml
reports/newman-lab05-compose.html
```

---

## 5. Dừng stack

Khi không cần nữa, dừng và xoá các container bằng:

```bash
docker compose down
```

Nếu muốn xoá volume dữ liệu của DB, thêm tuỳ chọn `-v`:

```bash
docker compose down -v
```

---

## 6. Lệnh nhanh

Bạn có thể dùng Makefile:

```bash
make compose-up
make compose-down
make logs
```

---

## 7. Mẹo gỡ lỗi

- Sử dụng `docker compose ps` để xem trạng thái container.
- Nếu API trả lỗi kết nối DB, hãy kiểm tra biến môi trường `POSTGRES_*` trong `.env` và đảm bảo DB đã sẵn sàng (`pg_isready`).
- Nếu AI service cần tải mô hình lớn, tăng `start_period` của healthcheck trong `docker-compose.yml`.