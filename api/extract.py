from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from doctr.models import ocr_predictor
from pdf2image import convert_from_bytes
import numpy as np

app = FastAPI()

# Carrega o modelo uma vez por cold-start
model = ocr_predictor(pretrained=True)

@app.post("/")
async def extract_text(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Apenas PDFs são suportados.")
    data = await file.read()
    try:
        images = convert_from_bytes(data, dpi=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao converter PDF: {e}")
    full_text = ""
    for img in images:
        img_np = np.array(img)
        result = model([img_np])
        for page in result.pages:
            for block in page.blocks:
                for line in block.lines:
                    line_text = " ".join([w.value for w in line.words])
                    full_text += line_text + "\n"
        full_text += "\n"
    return JSONResponse({"text": full_text})
