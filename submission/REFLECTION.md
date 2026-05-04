# Lab Reflection - Day 18: Lakehouse Architecture with Delta Lake

## 1. Path Selection
Tôi đã thực hiện bài lab này bằng **Spark Path (Docker)**. 
- **Môi trường:** Sử dụng Docker Compose để quản lý Spark, Jupyter Lab và MinIO (S3-compatible storage).
- **Lý do chọn:** Muốn trải nghiệm quy trình làm việc thực tế với Apache Spark và kiến trúc Medallion trong môi trường containerized.

## 2. Key Learnings & Impressions
Điều làm tôi ấn tượng nhất trong bài lab này là tính năng **OPTIMIZE + ZORDER** của Delta Lake:
- **Hiệu năng:** Trước khi optimize, việc truy vấn trên hàng trăm file nhỏ (Small-file problem) cực kỳ chậm. Sau khi chạy lệnh `OPTIMIZE`, tốc độ truy vấn tăng lên rõ rệt (hơn 3-10 lần tùy trường hợp).
- **Tính năng hữu ích khác:** Khả năng **Time Travel** (RESTORE về phiên bản cũ) rất ấn tượng, giúp xử lý các sự cố dữ liệu sai một cách nhanh chóng mà không cần backup thủ công phức tạp.

## 3. Challenges Faced
Khó khăn lớn nhất mà tôi gặp phải là lỗi **OutOfMemory (OOM)** trong quá trình tạo dữ liệu mẫu:
- **Vấn đề:** Khi chạy script tạo 1 triệu dòng dữ liệu (`make spark-data`), hệ thống bị treo do vượt quá giới hạn bộ nhớ Java Heap Space của Spark Driver.
- **Cách giải quyết:** 
    1. Đã thực hiện `Shut Down All Kernels` để giải phóng RAM đang bị chiếm dụng bởi các Notebook khác.
    2. Cấu hình lại script `generate_data.py` để sử dụng phương pháp tạo dữ liệu phân tán (distributed generation) thông qua `spark.range`, thay vì xây dựng list dữ liệu lớn trong RAM của Python.
    3. Sau khi tối ưu, script đã chạy thành công 1,000,000 dòng dữ liệu mà không gặp lỗi bộ nhớ.

## 4. Conclusion
Bài lab đã giúp tôi hiểu rõ sức mạnh của Delta Lake trong việc giải quyết các vấn đề kinh điển của Data Lake truyền thống như ACID transactions, Schema Enforcement và hiệu năng truy vấn. Kiến trúc Medallion (Bronze -> Silver -> Gold) thực sự là một mô hình quản lý dữ liệu khoa học và hiệu quả.
