# Day 18 — Lakehouse Lab (Track 2)

Lab cho **AICB-P2T2 · Ngày 18 · Data Lakehouse Architecture**.
Build Bronze → Silver → Gold pipeline với Delta Lake trên local object
storage (MinIO) — **không cần tài khoản cloud, không cần Databricks**.

---

## Quick Start (3 lệnh)

```bash
git clone https://github.com/VinUni-AI20k/Day18-Track2-Lakehouse-Lab.git
cd Day18-Track2-Lakehouse-Lab
make up && make smoke
```

Khi `make smoke` in ra `All checks passed`, mở **http://localhost:8888**
(token: `lakehouse`) và bắt đầu từ `notebooks/01_delta_basics.ipynb`.

> **First-time only:** lệnh `make up` sẽ pull ~2 GB Docker images (Spark + MinIO),
> sau đó cell đầu tiên sẽ download ~200 MB Maven JARs (Delta + Hadoop-AWS).
> Tất cả được cache lại — lần `make up` thứ hai chạy < 10 giây.

### Tất cả lệnh `make`

| Lệnh         | Tác dụng |
|--------------|----------|
| `make up`    | Start MinIO + Spark/Jupyter |
| `make smoke` | 30-second end-to-end smoke test |
| `make data`  | Generate 1M-row Bronze sample (cần cho NB4) |
| `make logs`  | Tail logs (debug) |
| `make down`  | Stop containers (data persists) |
| `make clean` | Stop **và xoá toàn bộ** MinIO data + cache (full reset) |
| `make shell` | Bash shell trong Spark container |

Không có `make`? Dùng trực tiếp: `docker compose -f docker/docker-compose.yml up -d`.

---

## Yêu cầu hệ thống

- **Docker Desktop** ≥ 4.x (Mac/Windows) hoặc Docker Engine ≥ 24 (Linux)
- **RAM** ≥ 8 GB free (Spark cần ~4 GB)
- **Disk** ≥ 10 GB free
- **Network** mở Maven Central (`repo1.maven.org`) — chỉ lần đầu

Đã test trên macOS 15 (Apple Silicon), Ubuntu 22.04, Windows 11 + WSL2.

---

## Cấu trúc & tiến trình

| Notebook | Skill | Slide section |
|---|---|---|
| `01_delta_basics.ipynb` | Write/read Delta, schema enforcement, transaction log | §2 Delta Lake |
| `02_optimize_zorder.ipynb` | Small-file problem; OPTIMIZE + ZORDER benchmark | §5 Storage Optimization |
| `03_time_travel.ipynb` | versionAsOf, RESTORE, MERGE, DESCRIBE HISTORY | §3 Time Travel |
| `04_medallion.ipynb` | LLM-observability Bronze→Silver→Gold pipeline | §6 Lakehouse cho AI/ML |

> Source files trong git là `.py` (Jupytext percent-format) — nhỏ, dễ review,
> không nuốt diff. Container tự động convert sang `.ipynb` lần đầu start.
> Chỉ chỉnh sửa `.ipynb` trong Jupyter; `make` sẽ keep them in sync.

---

## Endpoints

| URL | Service | Credentials |
|---|---|---|
| http://localhost:8888 | Jupyter Lab | token `lakehouse` |
| http://localhost:9001 | MinIO Console | `minioadmin` / `minioadmin` |
| http://localhost:4040 | Spark UI | (no auth, only when a notebook is running) |

---

## Deliverable (nộp 4 notebook đã chạy + ảnh chụp)

Mapping 1-to-1 với slide deliverable:

1. **NB1** — Delta table tạo, `_delta_log/00..0.json` xuất hiện trong MinIO.
2. **NB2** — Bảng so sánh query time TRƯỚC vs SAU `OPTIMIZE+ZORDER`. Mục tiêu ≥ 3×.
3. **NB3** — `DESCRIBE HISTORY` show ≥ 5 versions; RESTORE < 30 s; MERGE 100K rows.
4. **NB4** — Bronze + Silver + Gold tables tồn tại; Gold query ra metrics đúng.

Chấm điểm: xem [`rubric.md`](rubric.md). Tổng 100 pts → Track-2 Daily Lab (30%).

---

## Troubleshooting

| Triệu chứng | Nguyên nhân | Fix |
|---|---|---|
| `make up` báo "port 8888 in use" | Jupyter khác đang chạy | `lsof -i :8888` rồi kill, hoặc đổi port trong `docker/docker-compose.yml` |
| `make smoke` fail: `ClassNotFoundException: S3AFileSystem` | Maven JARs chưa download xong | Chạy lại `make smoke` — lần 2 sẽ thấy JARs trong `~/.ivy2` cache |
| `make smoke` fail: `Connection refused` MinIO | MinIO chưa ready | `make logs`, đợi `Buckets ready: lakehouse, bronze, silver, gold` |
| Jupyter báo "permission denied" khi save | UID mismatch giữa host/container | `make clean && make up` (reset volumes) |
| NB4 lỗi "Path does not exist: s3a://bronze" | Quên generate data | `make data` |
| Spark Out-of-Memory | Default 2 GB driver không đủ | Trong notebook trước khi tạo session: `os.environ["PYSPARK_SUBMIT_ARGS"] = "--driver-memory 4g pyspark-shell"` |
| Maven Central blocked (corp/uni network) | Firewall | Dùng `pip install --index-url …` proxy hoặc liên hệ TA để get pre-built JARs |

---

## Submission

Fork repo này thành `<your-username>/Day18-Track2-Lakehouse-Lab`, push:
1. 4 notebook đã chạy (committed với output cells)
2. `submission/screenshots/` — MinIO console show `_delta_log/` + buckets
3. `submission/REFLECTION.md` (≤ 200 words) — anti-pattern nào trong slide §5 team bạn dễ vướng nhất, vì sao?

PR back vào upstream với title `[NXX] Lab18 — <Họ Tên>`.

---

## License & Attribution
© VinUniversity AICB program. Phỏng theo Track 2 Day 18 slide.
