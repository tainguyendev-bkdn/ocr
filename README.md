# OCR Project - Nhận dạng văn bản từ hình ảnh

## Mô tả

Dự án OCR (Optical Character Recognition) nhận diện và trích xuất văn bản từ hình ảnh. Hệ thống hỗ trợ nhận dạng văn bản tiếng Việt và các ngôn ngữ khác từ các file PDF và PNG.

## Yêu cầu

### Input (Đầu vào)
- **PDF**: File PDF chứa hình ảnh hoặc văn bản
- **PNG**: File hình ảnh định dạng PNG

### Output (Đầu ra)
- **Text**: Văn bản được trích xuất từ hình ảnh sau khi thực hiện OCR

## Công nghệ sử dụng

- **VietOCR**: Thư viện OCR chuyên dụng cho tiếng Việt
- **PaddleOCR**: Thư viện OCR đa ngôn ngữ, hỗ trợ nhiều ngôn ngữ
- **PyMuPDF**: Xử lý và chuyển đổi file PDF
- **OpenCV & Pillow**: Xử lý hình ảnh
- **FastAPI**: Framework web để xây dựng API

## Cài đặt

1. Cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```

2. Cài đặt PaddlePaddle (nếu sử dụng PaddleOCR):
```bash
# CPU version
pip install paddlepaddle

# GPU version (nếu có GPU)
pip install paddlepaddle-gpu
```

## Sử dụng

### Xử lý file PDF
- Upload file PDF
- Hệ thống sẽ tự động chuyển đổi các trang PDF thành hình ảnh
- Thực hiện OCR trên từng trang
- Trả về văn bản đã được nhận dạng

### Xử lý file PNG
- Upload file PNG
- Thực hiện OCR trực tiếp trên hình ảnh
- Trả về văn bản đã được nhận dạng

## Quy trình xử lý

1. **Nhận input**: File PDF hoặc PNG
2. **Tiền xử lý**: 
   - Với PDF: Chuyển đổi từng trang thành hình ảnh
   - Với PNG: Tối ưu hóa hình ảnh (nếu cần)
3. **OCR**: Sử dụng VietOCR hoặc PaddleOCR để nhận dạng văn bản
4. **Hậu xử lý**: Làm sạch và định dạng văn bản đầu ra
5. **Output**: Trả về văn bản đã được trích xuất

## Lưu ý

- Đảm bảo hình ảnh có độ phân giải đủ cao để OCR hoạt động tốt
- Văn bản trong hình ảnh cần rõ ràng, không bị mờ hoặc nghiêng quá nhiều
- Hỗ trợ tốt nhất cho tiếng Việt, nhưng cũng có thể xử lý các ngôn ngữ khác

