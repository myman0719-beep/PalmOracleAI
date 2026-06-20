from pathlib import Path
import os
import shutil
import uuid

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from predict_palm import analyze_image

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)

app = FastAPI(
    title="Palm AI API",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


def build_details(scores):
    mapping = {
        "logic": {"title": "Tư duy Logic", "icon": "🧠"},
        "emotion": {"title": "Cảm xúc", "icon": "❤️"},
        "leadership": {"title": "Lãnh đạo", "icon": "👑"},
        "creativity": {"title": "Sáng tạo", "icon": "🎨"},
        "confidence": {"title": "Tự tin", "icon": "💪"},
        "social": {"title": "Xã hội", "icon": "🤝"},
        "determination": {"title": "Quyết tâm", "icon": "🔥"},
        "independence": {"title": "Độc lập", "icon": "🦅"}
    }

    descriptions = {
        "logic": {
            "high": "Bạn có tư duy phân tích mạnh, xử lý vấn đề có hệ thống.",
            "medium": "Bạn có khả năng suy luận tương đối tốt.",
            "low": "Bạn thường dựa nhiều vào trực giác hơn."
        },
        "emotion": {
            "high": "Bạn rất dễ đồng cảm và nhạy cảm.",
            "medium": "Bạn cân bằng khá tốt giữa lý trí và cảm xúc.",
            "low": "Bạn kiểm soát cảm xúc khá tốt."
        },
        "leadership": {
            "high": "Bạn có tố chất dẫn dắt và tổ chức.",
            "medium": "Bạn có khả năng lãnh đạo trong vài tình huống.",
            "low": "Bạn thích phối hợp hơn là đứng đầu."
        },
        "creativity": {
            "high": "Bạn có khả năng sáng tạo nổi bật.",
            "medium": "Bạn có tư duy linh hoạt.",
            "low": "Bạn thiên về tính thực tế."
        },
        "confidence": {
            "high": "Bạn khá tự tin trong hành động và quyết định.",
            "medium": "Bạn có mức tự tin tương đối ổn định.",
            "low": "Bạn thường cẩn trọng trước khi đưa ra quyết định."
        },
        "social": {
            "high": "Bạn giao tiếp tốt và dễ hòa nhập.",
            "medium": "Bạn có khả năng kết nối ở mức ổn.",
            "low": "Bạn thích không gian riêng tư hơn."
        },
        "determination": {
            "high": "Bạn có tinh thần bền bỉ và khó bỏ cuộc.",
            "medium": "Bạn có trách nhiệm và cố gắng khá tốt.",
            "low": "Bạn linh hoạt và dễ thay đổi khi gặp khó khăn."
        },
        "independence": {
            "high": "Bạn thích tự chủ và ra quyết định độc lập.",
            "medium": "Bạn có thể tự xử lý phần lớn công việc.",
            "low": "Bạn thích tham khảo ý kiến người khác."
        }
    }

    details = []
    for key, value in scores.items():
        if value >= 75:
            level = "CAO"
            bucket = "high"
        elif value >= 50:
            level = "TRUNG BÌNH"
            bucket = "medium"
        else:
            level = "THẤP"
            bucket = "low"

        details.append({
            "name": mapping[key]["title"],
            "icon": mapping[key]["icon"],
            "score": round(value, 1),
            "level": level,
            "description": descriptions[key][bucket]
        })

    return details


@app.get("/")
def home():
    return {"status": "running", "message": "Palm AI Backend active"}


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/analyze")
async def analyze_palm(file: UploadFile = File(...)):
    try:
        allowed = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
        if file.content_type not in allowed:
            raise HTTPException(status_code=400, detail="File phải là ảnh jpg, png hoặc webp")

        ext = file.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        file_path = UPLOAD_FOLDER / filename

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = analyze_image(str(file_path))

        try:
            os.remove(file_path)
        except:
            pass

        details = build_details(result["scores"])

        return JSONResponse(content={
            "success": True,
            "scores": result["scores"],
            "summary": result["summary"],
            "careers": result["careers"],
            "details": details,
            "analysis": result["analysis"],
            "report": result["report"],
            "features": result["features"]
        })

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)