# Vivita Assistant Chatbot

Vivita Assistant là chatbot tư vấn sản phẩm cho khách hàng, sử dụng AI để trả lời các câu hỏi về sản phẩm và dịch vụ dựa trên dữ liệu thực tế.

## Tính năng

- Tư vấn sản phẩm, dịch vụ Vivita bằng tiếng Việt.
- Tìm kiếm, trích xuất thông tin sản phẩm từ website vivita.vn.
- Giao diện chat hiện đại, responsive, hỗ trợ Markdown.
- Triển khai dễ dàng với Docker Compose.

## Cấu trúc dự án

```
.
├── backend/                # Backend FastAPI (Python)
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # Frontend React (Material-UI)
│   ├── src/
│   │   └── App.js
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml      # Quản lý multi-container
├── .env                    # Biến môi trường (API key, Redis)
└── README.md
```

## Yêu cầu

- Docker & Docker Compose
- (Tùy chọn) Node.js, Python 3.9+ nếu chạy thủ công

## Cài đặt & Chạy nhanh với Docker Compose

1. **Tạo file `.env` ở thư mục gốc:**

   ```env
   GENAI_API_KEY=YOUR_GOOGLE_GENAI_API_KEY
   REDIS_URL=redis://redis:6379/0
   ```

   (Thay `YOUR_GOOGLE_GENAI_API_KEY` bằng API key thực tế)
   
   ** Chạy trên terminal**
   `` echo "YOUR_GOOGLE_GENAI_API_KEY`nREDIS_URL=redis://redis:6379/0" | Out-File -FilePath .env -Encoding utf8 ``

3. **Build & chạy toàn bộ hệ thống:**

   ```bash
   docker-compose up --build
   ```

4. **Truy cập:**
   - Frontend: [http://localhost:3000](http://localhost:3000)
   - Backend API: [http://localhost:8001](http://localhost:8001)
   - Xem log: [http://localhost:9999](http://localhost:9999)

## Chạy thủ công (không dùng Docker)

### Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate  # hoặc .venv\Scripts\activate trên Windows
pip install -r requirements.txt
uvicorn app:app --reload --host 0.0.0.0 --port 8001
```

### Frontend

```bash
cd frontend
npm install
npm start
```

## Tuỳ chỉnh

- Sửa prompt hệ thống, logic AI: `backend/app.py`
- Sửa giao diện: `frontend/src/App.js`

## Đóng góp & bản quyền

- Dự án phục vụ mục đích demo.
- Mọi đóng góp, phản hồi xin gửi về đội ngũ phát triển.
