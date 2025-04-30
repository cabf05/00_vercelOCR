import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from doctr.models import ocr_predictor
from pdf2image import convert_from_bytes
import numpy as np

# Configura logging para STDOUT no Vercel
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Carrega o modelo apenas uma vez por cold-start
try:
    logger.info("Carregando modelo OCR docTR…")
    model = ocr_predictor(pretrained=True)
    logger.info("Modelo carregado com sucesso")
except Exception as e:
    logger.exception("Falha ao carregar o modelo no cold-start")
    # Não dá pra prosseguir sem o modelo
    raise

@app.post("/")
async def extract_text(file: UploadFile = File(...)):
    logger.info(f"Nova requisição: arquivo={file.filename}, content_type={file.content_type}")
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Apenas PDFs são suportados.")

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Arquivo vazio.")

    # Convertemos só a primeira página pra testar mais rápido
    try:
        images = convert_from_bytes(data, dpi=150, first_page=1, last_page=1)
        logger.info(f"convert_from_bytes retornou {len(images)} imagem(ns)")
    except Exception as e:
        logger.exception("Erro no convert_from_bytes")
        raise HTTPException(status_code=500, detail=f"Erro ao converter PDF: {e}")

    full_text = ""
    try:
        for img in images:
            img_np = np.array(img)
            result = model([img_np])
            for page in result.pages:
                for block in page.blocks:
                    for line in block.lines:
                        line_text = " ".join(w.value for w in line.words)
                        full_text += line_text + "\n"
            full_text += "\n"
        logger.info("OCR concluído sem exceções")
    except Exception as e:
        logger.exception("Erro durante OCR")
        raise HTTPException(status_code=500, detail=f"Erro ao processar OCR: {e}")

    return JSONResponse({"text": full_text})
