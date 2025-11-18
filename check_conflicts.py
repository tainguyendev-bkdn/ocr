"""
Script kiểm tra xung đột giữa các package
"""
import os
import sys
import subprocess
import pkg_resources

# Fix encoding cho Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

def check_package_version(package_name):
    """Kiểm tra version của một package"""
    try:
        version = pkg_resources.get_distribution(package_name).version
        return version
    except pkg_resources.DistributionNotFound:
        return "NOT INSTALLED"
    except Exception as e:
        return f"ERROR: {e}"

def check_all_packages():
    """Kiểm tra tất cả các package quan trọng"""
    print("=" * 60)
    print("KIEM TRA VERSION CAC PACKAGE")
    print("=" * 60)
    
    packages = {
        "paddleocr": "PaddleOCR",
        "paddlepaddle": "PaddlePaddle (CPU)",
        "paddlepaddle-gpu": "PaddlePaddle (GPU)",
        "numpy": "NumPy",
        "opencv-python": "OpenCV",
        "pillow": "Pillow",
        "vietocr": "VietOCR",
        "pymupdf": "PyMuPDF",
        "fastapi": "FastAPI",
        "uvicorn": "Uvicorn",
    }
    
    results = {}
    for package, name in packages.items():
        version = check_package_version(package)
        results[package] = version
        status = "[OK]" if version != "NOT INSTALLED" else "[X]"
        print(f"{status} {name:25} ({package:20}): {version}")
    
    return results

def check_compatibility():
    """Kiểm tra compatibility giữa các package"""
    print("\n" + "=" * 60)
    print("KIEM TRA COMPATIBILITY")
    print("=" * 60)
    
    results = check_all_packages()
    
    issues = []
    
    # Kiểm tra PaddleOCR và PaddlePaddle
    paddleocr_ver = results.get("paddleocr", "")
    paddle_ver = results.get("paddlepaddle", "")
    paddle_gpu_ver = results.get("paddlepaddle-gpu", "")
    
    if paddleocr_ver != "NOT INSTALLED":
        if paddle_ver == "NOT INSTALLED" and paddle_gpu_ver == "NOT INSTALLED":
            issues.append("[!] PaddleOCR can PaddlePaddle nhung khong tim thay!")
        elif paddle_gpu_ver != "NOT INSTALLED" and paddle_ver != "NOT INSTALLED":
            issues.append("[!] Ca PaddlePaddle CPU va GPU deu duoc cai - co the gay conflict!")
    
    # Kiểm tra NumPy version
    numpy_ver = results.get("numpy", "")
    if numpy_ver != "NOT INSTALLED":
        try:
            major, minor = map(int, numpy_ver.split('.')[:2])
            if major > 1 or (major == 1 and minor > 26):
                issues.append(f"[!] NumPy {numpy_ver} co the khong tuong thich voi PaddleOCR 2.7.2 (khuyen nghi <= 1.26.x)")
        except:
            pass
    
    # Kiểm tra OpenCV version
    opencv_ver = results.get("opencv-python", "")
    if opencv_ver != "NOT INSTALLED":
        try:
            major, minor = map(int, opencv_ver.split('.')[:2])
            if major != 4 or minor < 6:
                issues.append(f"[!] OpenCV {opencv_ver} co the khong tuong thich (requirements.txt yeu cau 4.6.0.66)")
        except:
            pass
    
    # Kiểm tra Python version
    python_ver = sys.version_info
    print(f"\nPython version: {python_ver.major}.{python_ver.minor}.{python_ver.micro}")
    if python_ver.major != 3 or python_ver.minor < 7:
        issues.append("[!] Python < 3.7 co the khong duoc ho tro tot")
    elif python_ver.minor > 11:
        issues.append("[!] Python > 3.11 co the co compatibility issues voi mot so packages")
    
    # Hiển thị issues
    if issues:
        print("\n" + "=" * 60)
        print("CAC VAN DE PHAT HIEN:")
        print("=" * 60)
        for issue in issues:
            print(issue)
    else:
        print("\n[OK] Khong phat hien van de compatibility ro rang")
    
    return issues

def check_onednn_related():
    """Kiểm tra các package liên quan đến OneDNN"""
    print("\n" + "=" * 60)
    print("KIEM TRA ONEDNN/MKLDNN RELATED PACKAGES")
    print("=" * 60)
    
    onednn_packages = [
        "mkl",
        "mkl-service",
        "intel-openmp",
        "onednn",
    ]
    
    found = []
    for package in onednn_packages:
        version = check_package_version(package)
        if version != "NOT INSTALLED":
            found.append((package, version))
            print(f"[!] {package:20}: {version} (co the gay conflict voi OneDNN)")
    
    if not found:
        print("[OK] Khong tim thay package OneDNN/MKL duoc cai rieng")
    else:
        print("\n[>] Cac package nay co the gay conflict voi PaddlePaddle OneDNN")
        print("   Neu gap loi OneDNN, thu uninstall cac package nay:")
        for pkg, ver in found:
            print(f"   pip uninstall {pkg}")

def check_environment_variables():
    """Kiểm tra các biến môi trường liên quan"""
    print("\n" + "=" * 60)
    print("KIEM TRA BIEN MOI TRUONG")
    print("=" * 60)
    
    env_vars = [
        "FLAGS_use_mkldnn",
        "FLAGS_use_gpu",
        "FLAGS_onednn",
        "MKLDNN_ENABLED",
        "USE_MKLDNN",
    ]
    
    for var in env_vars:
        value = os.environ.get(var, "NOT SET")
        status = "[OK]" if value in ["0", "False", "false"] else "[!]" if value != "NOT SET" else "[ ]"
        print(f"{status} {var:25}: {value}")

def main():
    """Main function"""
    print("\n" + "=" * 60)
    print("KIEM TRA CONFLICT VA COMPATIBILITY CUA PACKAGES")
    print("=" * 60 + "\n")
    
    # Kiểm tra packages
    check_all_packages()
    
    # Kiểm tra compatibility
    issues = check_compatibility()
    
    # Kiểm tra OneDNN packages
    check_onednn_related()
    
    # Kiểm tra environment variables
    check_environment_variables()
    
    # Tóm tắt
    print("\n" + "=" * 60)
    print("TOM TAT")
    print("=" * 60)
    
    if issues:
        print(f"[!] Phat hien {len(issues)} van de tiem an")
        print("\n[>] Khuyen nghi:")
        print("   1. Dam bao PaddlePaddle duoc cai dat dung version")
        print("   2. Kiem tra NumPy version (nen <= 1.26.x)")
        print("   3. Dam bao chi cai PaddlePaddle CPU HOAC GPU, khong cai ca hai")
        print("   4. Neu van loi OneDNN, thu:")
        print("      - pip uninstall paddlepaddle paddlepaddle-gpu")
        print("      - pip install paddlepaddle==2.5.2 (version on dinh hon)")
    else:
        print("[OK] Khong phat hien van de ro rang")
        print("\n[>] Neu van gap loi OneDNN:")
        print("   1. Dam bao da set du bien moi truong (xem ocr_engine.py)")
        print("   2. Thu downgrade PaddlePaddle ve version on dinh hon")
        print("   3. Kiem tra log chi tiet de xac dinh nguyen nhan")

if __name__ == "__main__":
    main()

