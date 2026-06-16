import pandas as pd
from loguru import logger
import sys
from modules.MakeRequisitions import MakeRequisitions
from modules.SaveData import SaveData

class PipelineUpdate:
    def __init__(
        self,
        excel_path: str,
        url_main: str,
        sheet_name: str
    ):
        self.excel_path = excel_path
        self.sheet_name = sheet_name
        self.url_main = url_main.rstrip('/') 

    def _read_excel(self) -> pd.DataFrame:
        """Lê um arquivo Excel e retorna um DataFrame."""
        try:
            df = pd.read_excel(self.excel_path, sheet_name=self.sheet_name)
            logger.info("📄 Arquivo de Input Excel lido com sucesso!")
            return df
        except Exception as e:
            logger.critical(f"❌ Erro fatal ao tentar ler o arquivo Excel de input: {e}")
            return pd.DataFrame()
    
    def execute_pipeline(self) -> None:
        df = self._read_excel()
        
        if df.empty:
            logger.critical("⛔ Pipeline interrompido: O DataFrame de input está vazio ou não pôde ser lido.")
            sys.exit(1)
            
        for index, row in df.iterrows():
            nome_endpoint = row['nome_tabela']
            webtoken = row['api_key']
            campo_data = row['campo_dt']
            
            logger.info(f"🔄 Iniciando extração do endpoint: {nome_endpoint}")
            
            headers = {
                'Content-Type': 'application/json',
                'Webtoken': webtoken
            }
            
            req = MakeRequisitions(
                url=self.url_main, 
                headers=headers, 
                endpoint_name=nome_endpoint, 
                field_date=campo_data
            )
            
            df_main, p1, p2 = req.make_req()  
            
            if df_main.empty:
                logger.warning(f"⚠️ Nenhuma informação válida para '{nome_endpoint}'. Realize a validação do step anterior.\nPulando para o próximo...")
                continue
            save = SaveData(
                df=df_main,
                name_table=nome_endpoint,
                field_filter=campo_data,
                period_min=p1,
                period_max=p2
            )
            save.save()
            
        logger.info("✅ Execução do pipeline finalizada em todos os endpoints.")
    
    
    