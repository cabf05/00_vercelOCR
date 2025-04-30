from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from onnxtr.models import ocr_predictor
from onnxtr.io import DocumentFile

app = FastAPI()

# Carrega o modelo uma vez por cold-start
model = ocr_predictor(pretrained=True)

@app.post("/")
async def extract_text(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Apenas PDFs são suportados.")
    data = await file.read()

    try:
        # Lê PDF direto para lista de páginas em np.ndarray
        pages = DocumentFile.from_pdf(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao ler PDF: {e}")

    full_text = ""
    try:
        # Executa OCR na lista de páginas
        result = model(pages)
        for page in result.pages:
            for block in page.blocks:
                for line in block.lines:
                    full_text += " ".join(w.value for w in line.words) + "\n"
            full_text += "\n"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no OCR: {e}")

    return JSONResponse({"text": full_text})
