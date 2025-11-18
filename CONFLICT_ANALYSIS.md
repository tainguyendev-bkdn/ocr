# Phân tích Conflict và Compatibility Issues

## Kết quả kiểm tra

Script `check_conflicts.py` đã được tạo để kiểm tra các vấn đề tiềm ẩn về compatibility và conflict giữa các packages.

## Các vấn đề đã được xử lý

### 1. OneDNN Error Fix
- ✅ Đã thêm nhiều biến môi trường để tắt OneDNN/MKLDNN trong `ocr_engine.py`
- ✅ Đã monkey patch `paddle.jit.save` để tránh lỗi khi export model
- ✅ Đã set flags trong Paddle trước khi import PaddleOCR

### 2. Package Versions
Các package hiện tại đều ở version phù hợp:
- NumPy: 1.26.4 ✅ (phù hợp với PaddleOCR 2.7.2)
- OpenCV: 4.6.0.66 ✅ (theo requirements.txt)
- Pillow: 10.2.0 ✅
- VietOCR: 0.3.11 ✅
- PyMuPDF: 1.23.26 ✅

## Các vấn đề tiềm ẩn cần lưu ý

### 1. PaddlePaddle Version
**Vấn đề**: PaddleOCR 2.7.2 cần PaddlePaddle tương thích, nhưng version cụ thể không được chỉ định trong requirements.txt

**Giải pháp**:
- Nên thêm PaddlePaddle vào requirements.txt với version cụ thể
- Khuyến nghị: `paddlepaddle==2.5.2` (version ổn định, ít lỗi OneDNN hơn)
- Hoặc: `paddlepaddle==2.6.0` (version mới hơn nhưng có thể có lỗi OneDNN)

### 2. Cài đặt cả CPU và GPU version
**Vấn đề**: Nếu cài cả `paddlepaddle` và `paddlepaddle-gpu` sẽ gây conflict

**Giải pháp**:
- Chỉ cài một trong hai:
  - CPU: `pip install paddlepaddle`
  - GPU: `pip install paddlepaddle-gpu`
- Nếu đã cài cả hai, uninstall một trong hai:
  ```bash
  pip uninstall paddlepaddle paddlepaddle-gpu
  pip install paddlepaddle  # hoặc paddlepaddle-gpu
  ```

### 3. NumPy Version
**Vấn đề**: NumPy > 1.26.x có thể không tương thích với PaddleOCR 2.7.2

**Giải pháp**:
- Giữ NumPy ở version 1.26.x hoặc thấp hơn
- Nếu đã upgrade, downgrade:
  ```bash
  pip install numpy==1.26.4
  ```

### 4. OneDNN/MKL Packages
**Vấn đề**: Các package như `mkl`, `mkl-service`, `intel-openmp` có thể conflict với PaddlePaddle OneDNN

**Giải pháp**:
- Nếu gặp lỗi OneDNN, thử uninstall các package này:
  ```bash
  pip uninstall mkl mkl-service intel-openmp onednn
  ```

### 5. Python Version
**Vấn đề**: 
- Python < 3.7: Không được hỗ trợ tốt
- Python > 3.11: Có thể có compatibility issues

**Giải pháp**:
- Sử dụng Python 3.7 - 3.11 (khuyến nghị: 3.10)

## Cách sử dụng script kiểm tra

Chạy script để kiểm tra conflicts:
```bash
python check_conflicts.py
```

Script sẽ:
1. Kiểm tra version của tất cả packages quan trọng
2. Phát hiện các vấn đề compatibility
3. Kiểm tra các package OneDNN/MKL có thể gây conflict
4. Kiểm tra các biến môi trường liên quan

## Khuyến nghị cài đặt

### Option 1: Version ổn định (khuyến nghị)
```bash
pip install paddlepaddle==2.5.2
pip install paddleocr==2.7.2
```

### Option 2: Version mới nhất
```bash
pip install paddlepaddle
pip install paddleocr==2.7.2
```

Sau đó chạy `check_conflicts.py` để kiểm tra.

## Nếu vẫn gặp lỗi OneDNN

1. **Đảm bảo đã set đủ biến môi trường** (đã được xử lý trong `ocr_engine.py`)

2. **Thử downgrade PaddlePaddle**:
   ```bash
   pip uninstall paddlepaddle paddlepaddle-gpu
   pip install paddlepaddle==2.5.2
   ```

3. **Kiểm tra log chi tiết** để xác định nguyên nhân cụ thể

4. **Thử uninstall các package OneDNN/MKL**:
   ```bash
   pip uninstall mkl mkl-service intel-openmp onednn
   ```

5. **Tạo môi trường ảo mới** và cài đặt lại từ đầu:
   ```bash
   python -m venv venv_ocr
   venv_ocr\Scripts\activate  # Windows
   pip install -r requirements.txt
   pip install paddlepaddle==2.5.2
   ```

## Tóm tắt

- ✅ Đã fix lỗi OneDNN trong code
- ✅ Đã tạo script kiểm tra conflicts
- ⚠️ Cần đảm bảo PaddlePaddle được cài đúng version
- ⚠️ Tránh cài cả CPU và GPU version cùng lúc
- ⚠️ Giữ NumPy ở version <= 1.26.x

