from lpmn_client import Task
import lpmn_client
import tempfile
import os
import zipfile
from typing import List

import pandas as pd


import pandas as pd

class ClarinService:

    def __init__(self, text: str, lmpn = 'any2txt|wcrft2|wsd|ccl_emo({"lang":"polish"})|ccl_emo_stats({"lang":"polish", "split_paragraphs": false}) ') -> None:
        self.text = text
        self.lmpn = lmpn

    def run(self) -> List:
        chunks = self._divide_text_into_chunks(self.text)
        total_chunks = len(chunks)
        print('File was devided into',len(chunks), "chunks")
        responses  = []
        joined = pd.DataFrame()
        for id, chunk in enumerate(chunks):
            print("Procesing chunk",(id + 1),"/", total_chunks)
            responses.append(self._send(chunk)) 
        return [pd.concat([joined, x]) for x in responses][0] 


    def _divide_text_into_chunks(self,text:str, min_len:int = 2000):

        chunks = []
        tmp = text
        while(tmp):
            if (len(tmp) > min_len):
                positon = tmp[:min_len].rfind('.')
                if ( positon == -1 ):
                    # If there is no dot, split on last whitespace
                    positon = tmp[:min_len].rfind(' ')
                    if (positon == -1 ):
                        # if there is not wihtie space should, split on min_len
                        positon = min_len
                chunks.append(tmp[:positon + 1].strip())
                tmp = tmp[positon + 1:]
            else:
                chunks.append(tmp.strip())
                tmp = tmp[min_len:]
        return chunks
         

    def _send(self,text):
        with tempfile.TemporaryDirectory() as tmpDir, tempfile.NamedTemporaryFile() as tmpfile:
            self._save_text_to_file(tmpfile.name, text) 
            self._send_file_to_clarin(tmpfile.name, tmpDir)
            resposne_as_xml_string = self._extract_response(tmpDir)
        return resposne_as_xml_string 
    
    def _save_text_to_file(self, path_to_file, text:str):
        print('Saving text to tmporary file')
        f = open(path_to_file,mode='r+')
        f.write(text)

    def _send_file_to_clarin(self, path_to_file, target_dir):
        print("File send to clarin service")
        task = Task(lpmn=self.lmpn)
        file_id = lpmn_client.upload_file(path_to_file)
        output_file_id = task.run(file_id)
        lpmn_client.download_file(output_file_id, target_dir)
        print("File succesfully recived")

    def _extract_response(self, outputdir):
        path_to_zip = os.path.join(outputdir,os.listdir(outputdir)[0])
        print('Unzipping file:', path_to_zip)
        zip_ref =  zipfile.ZipFile(path_to_zip, 'r')
        zip_ref.extractall(outputdir)
        un_ziped_path = os.path.join(outputdir,[file_name for file_name in os.listdir(outputdir) if 'zip' not in file_name][0])
        print('Reading from unzippedfile:', un_ziped_path) 
        return pd.read_csv(un_ziped_path, sep=';' )



    

    