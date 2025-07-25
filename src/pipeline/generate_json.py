from dataclasses import dataclass
import uuid
from fastapi import UploadFile
from components.data_ingestion import DataIngestion
import os
from llms.chat_fail_over_proxy import ChatFailOverProxy
from constants import *
from prompts.base_prompt import SYSTEM_PROPMT,SANITIZE_SYSTEM_PROMPT
import json


@dataclass
class GenerateJSONConfig():
    pass


class GenerateJSONPipeline():

    def __init__(self):
        pass

    @staticmethod
    async def run_pipeline(file : UploadFile ,schema : UploadFile):
        file_id = uuid.uuid4()
        file_type = file.filename.split(".")[-1]
        ingestor = DataIngestion()
        entities = await ingestor.initiate_DataIngestion(file_type=file_type,file=file,file_id=file_id)
        cfop = ChatFailOverProxy()
        content = await schema.read()
        json_data = json.loads(content.decode()) 
        json_string = json.dumps(json_data, indent=2)
        print(entities)
        if isinstance(entities ,list):
            dirty_json = list()
            for chunk in entities:
                pro = SYSTEM_PROPMT.replace("<schema>" , json_string).replace("<raw_text>" , f"CHUNKS : {json.dumps(chunk , indent=2)}")
                dirty_json.append(cfop.generate(OVERALL_MODEL,pro,3000,0.7,"json_object",100))
            pronoob  = SANITIZE_SYSTEM_PROMPT.replace("<schema>" , json_string).replace("<raw_text>" , json.dumps(dirty_json , indent=2))
            return cfop.generate(OVERALL_MODEL,pronoob,3000,0.7,"json_object",100)
        elif isinstance(entities , str):
            prompt = SYSTEM_PROPMT.replace("<schema>" , json_string).replace("<raw_text>" , entities)
            return cfop.generate(OVERALL_MODEL,prompt,3000,0.7,"json_object",100)
        return "Not processed now"
            
        