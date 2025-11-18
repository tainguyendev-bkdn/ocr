from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from ocr_engine import OCREngine
import os
import tempfile
import uvicorn

app = FastAPI(
    title="OCR API",
    description="API nhận dạng văn bản từ hình ảnh PDF và PNG",
    version="1.0.0"
)

# Khởi tạo OCR Engine (chỉ một lần khi khởi động)
ocr_engine = None

@app.on_event("startup")
async def startup_event():
    """Khởi tạo OCR Engine khi server khởi động"""
    global ocr_engine
    print("🚀 Starting OCR API Server...")
    ocr_engine = OCREngine()
    print("✅ Server ready!")

@app.get("/")
async def root():
    """Endpoint kiểm tra trạng thái server"""
    return {
        "message": "OCR API đang hoạt động",
        "endpoints": {
            "/ocr/image": "Upload file PNG/JPG để OCR",
            "/ocr/pdf": "Upload file PDF để OCR",
            "/ocr/auto": "Upload file tự động nhận diện (PDF/PNG/JPG)"
        }
    }

@app.post("/ocr/image")
async def ocr_image(file: UploadFile = File(...)):
    """
    OCR file hình ảnh (PNG, JPG, JPEG)
    """
    # Kiểm tra định dạng file
    allowed_extensions = ['.png', '.jpg', '.jpeg']
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Định dạng file không được hỗ trợ. Chỉ chấp nhận: {', '.join(allowed_extensions)}"
        )
    
    # Lưu file tạm
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_path = tmp_file.name
    
    try:
        # Thực hiện OCR
        text = ocr_engine.ocr_image(tmp_path)
        
        return JSONResponse({
            "success": True,
            "filename": file.filename,
            "file_type": "image",
            "text": text,
            "text_length": len(text)
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi xử lý OCR: {str(e)}")
    finally:
        # Xóa file tạm
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

@app.post("/ocr/pdf")
async def ocr_pdf(file: UploadFile = File(...)):
    """
    OCR file PDF
    """
    # Kiểm tra định dạng file
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext != '.pdf':
        raise HTTPException(
            status_code=400,
            detail="Định dạng file không được hỗ trợ. Chỉ chấp nhận file PDF."
        )
    
    # Lưu file tạm
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_path = tmp_file.name
    
    try:
        # Thực hiện OCR
        text = ocr_engine.ocr_pdf(tmp_path)
        
        return JSONResponse({
            "success": True,
            "filename": file.filename,
            "file_type": "pdf",
            "text": text,
            "text_length": len(text)
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi xử lý OCR: {str(e)}")
    finally:
        # Xóa file tạm
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

@app.post("/ocr/auto")
async def ocr_auto(file: UploadFile = File(...)):
    """
    OCR file tự động nhận diện định dạng (PDF, PNG, JPG, JPEG)
    """
    file_ext = os.path.splitext(file.filename)[1].lower()
    allowed_extensions = ['.pdf', '.png', '.jpg', '.jpeg']
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Định dạng file không được hỗ trợ. Chỉ chấp nhận: {', '.join(allowed_extensions)}"
        )
    
    # Lưu file tạm
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_path = tmp_file.name
    
    try:
        # Thực hiện OCR tự động
        text = ocr_engine.process_file(tmp_path)
        
        return JSONResponse({
            "success": True,
            "filename": file.filename,
            "file_type": file_ext[1:],  # Bỏ dấu chấm
            "text": text,
            "text_length": len(text)
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi xử lý OCR: {str(e)}")
    finally:
        # Xóa file tạm
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

