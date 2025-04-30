from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from doctr.models import ocr_predictor
from doctr.io import DocumentFile

app = FastAPI()

# Carrega o modelo apenas uma vez no cold-start da Function
model = ocr_predictor(pretrained=True)

@app.post("/")
async def extract_text(file: UploadFile = File(...)):
    # Valida tipo de conteúdo
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Apenas PDFs são suportados.")
    data = await file.read()

    # Converte PDF em lista de imagens (numpy arrays) sem precisar de Poppler
    try:
        pages = DocumentFile.from_pdf(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao ler PDF: {e}")

    # Executa OCR sobre todas as páginas
    full_text = ""
    try:
        result = model(pages)
        for page in result.pages:
            for block in page.blocks:
                for line in block.lines:
                    line_text = " ".join(word.value for word in line.words)
                    full_text += line_text + "\n"
            full_text += "\n"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no OCR: {e}")

    return JSONResponse({"text": full_text})
