from paddleocr import PaddleOCR
from vietocr.tool.config import Cfg
from vietocr.tool.predictor import Predictor
from PIL import Image
import fitz  # PyMuPDF
import cv2
import numpy as np
import os
import tempfile
import io
from typing import List, Union

class OCREngine:
    def __init__(self):
        print("🔄 Loading PaddleOCR (detector + layout)...")
        # Dùng PaddleOCR để detect vùng text (và có luôn rec nhưng mình không dùng)
        self.paddle = PaddleOCR(
            lang='vi',
            use_angle_cls=True
        )

        print("🔄 Loading VietOCR (recognizer)...")
        config = Cfg.load_config_from_name('vgg_transformer')
        config['device'] = 'cpu'  # nếu có GPU rồi hãy sửa thành 'cuda'
        self.vietocr = Predictor(config)

        print("✅ OCR Engine Ready")

    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Tiền xử lý hình ảnh để tối ưu hóa cho OCR.
        """
        # Chuyển sang numpy array để xử lý với OpenCV
        img_array = np.array(image.convert('RGB'))
        
        # Chuyển đổi sang grayscale nếu cần
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Tăng độ tương phản
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # Chuyển lại về PIL Image
        return Image.fromarray(enhanced)

    def _postprocess_text(self, text: str) -> str:
        """
        Hậu xử lý văn bản: làm sạch và định dạng.
        """
        # Loại bỏ khoảng trắng thừa
        text = ' '.join(text.split())
        
        # Loại bỏ ký tự đặc biệt không cần thiết (giữ lại dấu câu tiếng Việt)
        # Có thể thêm các quy tắc khác tùy nhu cầu
        
        return text.strip()

    def _pdf_to_images(self, pdf_path: str) -> List[Image.Image]:
        """
        Chuyển đổi các trang PDF thành hình ảnh.
        """
        images = []
        doc = fitz.open(pdf_path)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            # Render với độ phân giải cao (zoom = 2.0 tương đương 144 DPI)
            mat = fitz.Matrix(2.0, 2.0)
            pix = page.get_pixmap(matrix=mat)
            
            # Chuyển đổi sang PIL Image
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            images.append(img)
        
        doc.close()
        return images

    def ocr_image(self, image_path: str) -> str:
        """
        OCR 1 ảnh (PNG, JPG...), trả về text tiếng Việt.
        """
        print(f"📄 Processing image: {image_path}")
        
        # Mở và tiền xử lý hình ảnh
        pil_img = Image.open(image_path).convert("RGB")
        pil_img = self._preprocess_image(pil_img)
        
        # Lưu tạm để PaddleOCR xử lý
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            pil_img.save(tmp_file.name)
            tmp_path = tmp_file.name
        
        try:
            result = self.paddle.ocr(tmp_path, cls=True)
            
            lines = []
            
            # result[0] = kết quả của ảnh đầu tiên
            if result and result[0]:
                for line in result[0]:
                    box = line[0]  # 4 điểm [x,y]
                    xs = [pt[0] for pt in box]
                    ys = [pt[1] for pt in box]
                    
                    x1, x2 = int(min(xs)), int(max(xs))
                    y1, y2 = int(min(ys)), int(max(ys))
                    
                    crop = pil_img.crop((x1, y1, x2, y2))
                    
                    # Recognize bằng VietOCR
                    text = self.vietocr.predict(crop)
                    text = self._postprocess_text(text)
                    if text:
                        lines.append(text)
            
            return "\n".join(lines)
        finally:
            # Xóa file tạm
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def ocr_pdf(self, pdf_path: str) -> str:
        """
        OCR file PDF, trả về text từ tất cả các trang.
        """
        print(f"📄 Processing PDF: {pdf_path}")
        
        # Chuyển đổi PDF thành hình ảnh
        images = self._pdf_to_images(pdf_path)
        
        all_texts = []
        
        for idx, img in enumerate(images):
            print(f"  Processing page {idx + 1}/{len(images)}")
            
            # Lưu tạm hình ảnh để xử lý
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                img.save(tmp_file.name)
                tmp_path = tmp_file.name
            
            try:
                # OCR từng trang
                page_text = self.ocr_image(tmp_path)
                if page_text:
                    all_texts.append(f"--- Trang {idx + 1} ---\n{page_text}")
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
        
        return "\n\n".join(all_texts)

    def process_file(self, file_path: str) -> str:
        """
        Xử lý file tự động dựa vào định dạng (PDF hoặc PNG).
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.pdf':
            return self.ocr_pdf(file_path)
        elif file_ext in ['.png', '.jpg', '.jpeg']:
            return self.ocr_image(file_path)
        else:
            raise ValueError(f"Định dạng file không được hỗ trợ: {file_ext}")
