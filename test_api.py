"""
Script test API OCR
Sử dụng requests để test các endpoints
"""
import requests
import os
import sys

API_BASE_URL = "http://localhost:8000"

def test_root():
    """Test endpoint root"""
    print("=" * 60)
    print("Test: GET /")
    print("=" * 60)
    try:
        response = requests.get(f"{API_BASE_URL}/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        print()
        return True
    except Exception as e:
        print(f"Lỗi: {e}")
        print()
        return False

def test_ocr_image(image_path: str):
    """Test OCR file hình ảnh"""
    print("=" * 60)
    print(f"Test: POST /ocr/image với file {image_path}")
    print("=" * 60)
    
    if not os.path.exists(image_path):
        print(f"❌ File không tồn tại: {image_path}")
        print()
        return False
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': (os.path.basename(image_path), f, 'image/png')}
            response = requests.post(f"{API_BASE_URL}/ocr/image", files=files)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result['success']}")
            print(f"📄 Filename: {result['filename']}")
            print(f"📝 Text Length: {result['text_length']} characters")
            print(f"\n📋 Extracted Text:\n{'-' * 60}")
            print(result['text'])
            print('-' * 60)
        else:
            print(f"❌ Error: {response.text}")
        print()
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        print()
        return False

def test_ocr_pdf(pdf_path: str):
    """Test OCR file PDF"""
    print("=" * 60)
    print(f"Test: POST /ocr/pdf với file {pdf_path}")
    print("=" * 60)
    
    if not os.path.exists(pdf_path):
        print(f"❌ File không tồn tại: {pdf_path}")
        print()
        return False
    
    try:
        with open(pdf_path, 'rb') as f:
            files = {'file': (os.path.basename(pdf_path), f, 'application/pdf')}
            response = requests.post(f"{API_BASE_URL}/ocr/pdf", files=files)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result['success']}")
            print(f"📄 Filename: {result['filename']}")
            print(f"📝 Text Length: {result['text_length']} characters")
            print(f"\n📋 Extracted Text:\n{'-' * 60}")
            print(result['text'][:500] + "..." if len(result['text']) > 500 else result['text'])
            print('-' * 60)
        else:
            print(f"❌ Error: {response.text}")
        print()
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        print()
        return False

def test_ocr_auto(file_path: str):
    """Test OCR tự động nhận diện"""
    print("=" * 60)
    print(f"Test: POST /ocr/auto với file {file_path}")
    print("=" * 60)
    
    if not os.path.exists(file_path):
        print(f"❌ File không tồn tại: {file_path}")
        print()
        return False
    
    try:
        file_ext = os.path.splitext(file_path)[1].lower()
        content_type = 'application/pdf' if file_ext == '.pdf' else 'image/png'
        
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, content_type)}
            response = requests.post(f"{API_BASE_URL}/ocr/auto", files=files)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result['success']}")
            print(f"📄 Filename: {result['filename']}")
            print(f"📁 File Type: {result['file_type']}")
            print(f"📝 Text Length: {result['text_length']} characters")
            print(f"\n📋 Extracted Text:\n{'-' * 60}")
            text_preview = result['text'][:500] + "..." if len(result['text']) > 500 else result['text']
            print(text_preview)
            print('-' * 60)
        else:
            print(f"❌ Error: {response.text}")
        print()
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        print()
        return False

def main():
    """Hàm main để chạy các test"""
    print("\n" + "🚀 BẮT ĐẦU TEST OCR API" + "\n")
    
    # Test root endpoint
    if not test_root():
        print("❌ Server không phản hồi. Đảm bảo server đang chạy tại http://localhost:8000")
        return
    
    # Kiểm tra tham số dòng lệnh
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.pdf':
            test_ocr_pdf(file_path)
            test_ocr_auto(file_path)
        elif file_ext in ['.png', '.jpg', '.jpeg']:
            test_ocr_image(file_path)
            test_ocr_auto(file_path)
        else:
            print(f"❌ Định dạng file không được hỗ trợ: {file_ext}")
    else:
        print("💡 Cách sử dụng:")
        print("  python test_api.py <đường_dẫn_file>")
        print("\nVí dụ:")
        print("  python test_api.py example.png")
        print("  python test_api.py document.pdf")
        print("\nHoặc chỉ test endpoint root:")
        print("  python test_api.py")

if __name__ == "__main__":
    main()

