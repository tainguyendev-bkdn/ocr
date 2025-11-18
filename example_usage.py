"""
Ví dụ sử dụng OCR Engine
"""
from ocr_engine import OCREngine

def main():
    # Khởi tạo OCR Engine
    print("Khởi tạo OCR Engine...")
    engine = OCREngine()
    
    # Ví dụ 1: OCR file PNG
    print("\n" + "="*50)
    print("Ví dụ 1: OCR file PNG")
    print("="*50)
    try:
        image_path = "image.png"  # Thay bằng đường dẫn file PNG của bạn
        if os.path.exists(image_path):
            text = engine.ocr_image(image_path)
            print(f"\nKết quả OCR:\n{text}")
        else:
            print(f"File {image_path} không tồn tại. Vui lòng thay bằng đường dẫn file thực tế.")
    except Exception as e:
        print(f"Lỗi: {e}")
    
    # Ví dụ 2: OCR file PDF
    print("\n" + "="*50)
    print("Ví dụ 2: OCR file PDF")
    print("="*50)
    try:
        pdf_path = r"D:\AVE\CV\vca.pdf" # Thay bằng đường dẫn file PDF của bạn
        if os.path.exists(pdf_path):
            text = engine.ocr_pdf(pdf_path)
            print(f"\nKết quả OCR:\n{text}")
        else:
            print(f"File {pdf_path} không tồn tại. Vui lòng thay bằng đường dẫn file thực tế.")
    except Exception as e:
        print(f"Lỗi: {e}")
    
    # Ví dụ 3: Tự động nhận diện định dạng
    print("\n" + "="*50)
    print("Ví dụ 3: Tự động nhận diện định dạng")
    print("="*50)
    try:
        file_path = r"D:\AVE\CV\vca.pdf"  # hoặc PNG/JPG  
        if os.path.exists(file_path):
            text = engine.process_file(file_path)
            print(f"\nKết quả OCR:\n{text}")
        else:
            print(f"File {file_path} không tồn tại. Vui lòng thay bằng đường dẫn file thực tế.")
    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    import os
    main()

