from fastapi import FastAPI, UploadFile, File
from components.smol_dockling import extract_entities_from_pdf
from components.data_ingestion import DataIngestion
import shutil
import os
import uuid
from pipeline.generate_json import GenerateJSONPipeline
from fastapi.responses import StreamingResponse
import json
import io

app = FastAPI()

@app.post("/generate-json/")
async def parse_pdf(file: UploadFile = File(...),schema:UploadFile=File(...)):
    raw_response = await GenerateJSONPipeline.run_pipeline(file, schema)
    print(raw_response)
    if isinstance(raw_response, str):
        try:
            response_dict = json.loads(raw_response)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON format in response"}
    else:
        response_dict = raw_response
    json_data = json.dumps(response_dict, indent=2)
    json_bytes_io = io.BytesIO(json_data.encode("utf-8"))
    return StreamingResponse(
        json_bytes_io,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={file.filename}_processed.json"}
    )