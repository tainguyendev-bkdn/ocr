import os
import io
import tempfile
from typing import List

# Tắt MKLDNN & GPU & OneDNN để tránh lỗi OneDNN
# Phải set TRƯỚC khi import bất kỳ thứ gì từ Paddle
os.environ["FLAGS_use_mkldnn"] = "0"
os.environ["FLAGS_use_gpu"] = "0"
os.environ["FLAGS_onednn"] = "0"
os.environ["MKLDNN_ENABLED"] = "0"
os.environ["USE_MKLDNN"] = "0"
# Tắt OneDNN fusion operations
os.environ["FLAGS_use_mkldnn_fc"] = "0"
os.environ["FLAGS_use_mkldnn_bf16"] = "0"
# Tắt các optimization có thể trigger OneDNN
os.environ["FLAGS_use_cudnn"] = "0"
os.environ["FLAGS_cudnn_deterministic"] = "0"
# Tắt JIT compilation có thể gây lỗi OneDNN
os.environ["FLAGS_enable_jit"] = "0"
os.environ["FLAGS_jit_compile"] = "0"
# Tắt các tính năng optimization khác
os.environ["FLAGS_use_mkldnn_quantizer"] = "0"

# Import paddle và set flags trước khi import PaddleOCR
try:
    import paddle
    paddle.set_device('cpu')
    # Tắt OneDNN trong Paddle
    if hasattr(paddle, 'set_flags'):
        paddle.set_flags({'FLAGS_use_mkldnn': False})
    
    # Monkey patch paddle.jit.save để tránh lỗi OneDNN khi export model
    # (PaddleOCR có thể tự động cố gắng export model)
    original_jit_save = None
    if hasattr(paddle, 'jit') and hasattr(paddle.jit, 'save'):
        original_jit_save = paddle.jit.save
        def patched_jit_save(*args, **kwargs):
            # Nếu có lỗi OneDNN, bỏ qua việc export
            try:
                return original_jit_save(*args, **kwargs)
            except Exception as e:
                if "OneDnnContext" in str(e) or "onednn" in str(e).lower():
                    print(f"⚠️ Bỏ qua export model do lỗi OneDNN: {e}")
                    return None
                raise
        paddle.jit.save = patched_jit_save
except Exception as e:
    print(f"⚠️ Không thể set flags Paddle: {e}")

from paddleocr import PaddleOCR
from vietocr.tool.config import Cfg
from vietocr.tool.predictor import Predictor
from PIL import Image
import fitz  # PyMuPDF
import cv2
import numpy as np


class OCREngine:
    def __init__(self):
        print("🔄 Loading PaddleOCR (detector + layout)...")
        # Dùng PaddleOCR để detect vùng text (có luôn rec nhưng mình chỉ dùng detect)
        # Tắt hoàn toàn OneDNN/MKLDNN để tránh lỗi
        try:
            self.paddle = PaddleOCR(
                lang="vi",
                use_angle_cls=True,
                use_gpu=False,
                enable_mkldnn=False,  # rất quan trọng với CPU
                use_pdserving=False,
                use_tensorrt=False,
                ir_optim=False,  # Tắt IR optimization có thể liên quan đến OneDNN
                show_log=False,  # Tắt log để tránh một số vấn đề
            )
        except Exception as e:
            # Nếu vẫn lỗi, thử với các tham số tối thiểu
            print(f"⚠️ Lỗi khi khởi tạo với tham số đầy đủ: {e}")
            print("🔄 Thử khởi tạo với tham số tối thiểu...")
            self.paddle = PaddleOCR(
                lang="vi",
                use_angle_cls=False,  # Tắt angle classifier
                use_gpu=False,
                enable_mkldnn=False,
            )

        print("🔄 Loading VietOCR (recognizer)...")
        config = Cfg.load_config_from_name("vgg_transformer")
        config["device"] = "cpu"  # nếu có GPU thì đổi thành 'cuda'
        self.vietocr = Predictor(config)

        print("✅ OCR Engine Ready")

    # ----------------- TIỀN XỬ LÝ ẢNH -----------------
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Tiền xử lý hình ảnh để tối ưu cho OCR.
        """
        img_array = np.array(image.convert("RGB"))

        # Chuyển sang grayscale
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

        # Tăng độ tương phản với CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)

        return Image.fromarray(enhanced)

    def _postprocess_text(self, text: str) -> str:
        """
        Hậu xử lý văn bản: làm sạch và định dạng.
        """
        text = " ".join(text.split())
        return text.strip()

    # ----------------- CORE: OCR 1 PIL IMAGE -----------------
    def _ocr_pil_image(self, pil_img: Image.Image) -> str:
        """
        Nhận một PIL Image, chạy Paddle detect + VietOCR recog.
        """
        # Tiền xử lý
        pil_img = self._preprocess_image(pil_img)

        # PaddleOCR nhận numpy / path đều được → dùng numpy cho đỡ phải lưu file tạm
        img_np = np.array(pil_img)
        result = self.paddle.ocr(img_np, cls=True)

        lines = []
        if result and result[0]:
            for line in result[0]:
                box = line[0]  # 4 điểm [x, y]
                xs = [pt[0] for pt in box]
                ys = [pt[1] for pt in box]

                x1, x2 = int(min(xs)), int(max(xs))
                y1, y2 = int(min(ys)), int(max(ys))

                crop = pil_img.crop((x1, y1, x2, y2))

                text = self.vietocr.predict(crop)
                text = self._postprocess_text(text)
                if text:
                    lines.append(text)

        return "\n".join(lines)

    # ----------------- ẢNH -----------------
    def ocr_image(self, image_path: str) -> str:
        """
        OCR 1 ảnh (PNG, JPG...), trả về text tiếng Việt.
        """
        print(f"📄 Processing image: {image_path}")
        pil_img = Image.open(image_path).convert("RGB")
        return self._ocr_pil_image(pil_img)

    # ----------------- PDF → LIST PIL IMAGES -----------------
    def _pdf_to_images(self, pdf_path: str) -> List[Image.Image]:
        """
        Chuyển đổi các trang PDF thành hình ảnh.
        """
        images: List[Image.Image] = []
        doc = fitz.open(pdf_path)

        for page_num in range(len(doc)):
            page = doc[page_num]
            # zoom 2.0 ~ 144 DPI, đủ nét
            mat = fitz.Matrix(2.0, 2.0)
            pix = page.get_pixmap(matrix=mat)

            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data)).convert("RGB")

            # Giới hạn kích thước để tránh quá to làm Paddle lỗi
            max_side = 2000
            w, h = img.size
            scale = min(max_side / max(w, h), 1.0)
            if scale < 1.0:
                img = img.resize(
                    (int(w * scale), int(h * scale)), Image.LANCZOS
                )

            images.append(img)

        doc.close()
        return images

    # ----------------- PDF -----------------
    def ocr_pdf(self, pdf_path: str) -> str:
        """
        OCR file PDF, trả về text từ tất cả các trang.
        """
        print(f"📄 Processing PDF: {pdf_path}")

        images = self._pdf_to_images(pdf_path)
        all_texts = []

        for idx, img in enumerate(images):
            print(f"  Processing page {idx + 1}/{len(images)}")
            page_text = self._ocr_pil_image(img)
            if page_text:
                all_texts.append(f"--- Trang {idx + 1} ---\n{page_text}")

        return "\n\n".join(all_texts)

    # ----------------- AUTO -----------------
    def process_file(self, file_path: str) -> str:
        """
        Tự nhận định dạng (PDF / PNG / JPG / JPEG) và OCR.
        """
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            return self.ocr_pdf(file_path)
        elif ext in [".png", ".jpg", ".jpeg"]:
            return self.ocr_image(file_path)
        else:
            raise ValueError(f"Định dạng file không được hỗ trợ: {ext}")
