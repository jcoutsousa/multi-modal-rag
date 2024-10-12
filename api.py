from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List
import os
from main import extract_pdf_elements, categorize_elements, generate_text_summaries, generate_img_summaries, create_multi_vector_retriever, multi_modal_rag_chain
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from fastapi.staticfiles import StaticFiles
import logging
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the static directory
app.mount("/static", StaticFiles(directory="static"), name="static")



# Add this new route to serve the index.html
@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

# Serve static files
@app.get("/{filename}")
async def serve_static(filename: str):
    file_path = os.path.join("static", filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "File not found"}

class Query(BaseModel):
    question: str

@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Save the uploaded file
    file_path = f"uploads/{file.filename}"
    os.makedirs("uploads", exist_ok=True)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    
    # Process the PDF
    raw_pdf_elements = extract_pdf_elements("uploads/", file.filename)
    texts, tables = categorize_elements(raw_pdf_elements)
    text_summaries, table_summaries = generate_text_summaries(texts, tables, summarize_texts=True)
    img_base64_list, image_summaries = generate_img_summaries("uploads/")
    
    # Create vectorstore and retriever
    vectorstore = Chroma(collection_name="mm_rag_api", embedding_function=OpenAIEmbeddings())
    retriever = create_multi_vector_retriever(
        vectorstore, text_summaries, texts, table_summaries, tables, image_summaries, img_base64_list
    )
    
    # Create RAG chain
    global chain_multimodal_rag
    chain_multimodal_rag = multi_modal_rag_chain(retriever)
    try:
        contents = await file.read()
        # Here you would typically save the file or process it
        # For this example, we'll just return a success message
        return {"filename": file.filename, "message": "File uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


    
    return {"message": "PDF processed successfully"}

@app.post("/query/")
async def query(query: Query):
    if not chain_multimodal_rag:
        raise HTTPException(status_code=400, detail="Please upload a PDF first")
    
    response = chain_multimodal_rag.invoke(query.question)
    return {"response": response}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
