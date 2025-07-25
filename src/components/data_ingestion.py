from logger import logging
from exception import CustomException
import os
import sys
from dataclasses import dataclass
from fastapi import UploadFile
import shutil
from .smol_dockling import extract_entities_from_pdf
import csv



class DataIngestion:
    def __init__(self) -> None:
        pass
    
    async def initiate_DataIngestion(self,file_type, file : UploadFile ,file_id:str):
        logging.info('Entered Data Ingestion Component')
        temp_file_path = f"/tmp/{file_id}.{file_type}"
        try:
            if file_type == "csv":
                return self.parse_csv(file,temp_file_path , 100)
            elif file_type == "pdf":
                return self.parse_pdf(file ,temp_file_path)
            elif file_type in ['txt', 'md']:
                return await self.parse_raw(file ,temp_file_path)
            return "File type not supported yet"
        except Exception as e:
            raise CustomException(e,sys)

    async def parse_raw(self,file:UploadFile,path:str):
        contents = await file.read()
        return contents.decode("utf-8")

    def parse_csv(self,file:UploadFile,path:str,chunk_size=100):
        chunks = []
        with open(path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            chunk = []

            for row in reader:
                chunk.append(row)
                if len(chunk) == chunk_size:
                    chunks.append(chunk)
                    chunk = []
            if chunk:
                chunks.append(chunk)

        return chunks

    def parse_pdf(self,file:UploadFile,path:str):
        with open(path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        entities = extract_entities_from_pdf(path)
        os.remove(path)
        return entities
        
        

if __name__ == '__main__':
    pass