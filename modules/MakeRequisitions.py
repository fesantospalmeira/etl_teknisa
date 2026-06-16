import requests as r
import pandas as pd
from loguru import logger

class MakeRequisitions:
    def __init__(
        self,
        url: str,
        headers: dict,
        endpoint_name: str,
        field_date: str
    ):
        self.url = url
        self.headers = headers
        self.endpoint_name = endpoint_name
        self.field_date = field_date
    
    def make_req(self) -> tuple:
        """Função principal que realiza as requisições e retorna (DataFrame, Data_Min, Data_Max)."""
        logger.info(f"Iniciando requisição para o endpoint: {self.endpoint_name}.")
        
        try:
            response = r.get(url=self.url, headers=self.headers, timeout=500) 

            if response.status_code != 200:
                logger.error(f'❌ Erro HTTP {response.status_code} em {self.endpoint_name}')
                logger.error(f'❌ {response.text[:100]}')
               
                return pd.DataFrame(), None, None
            
            try:
                data = response.json()
                df = pd.DataFrame(data)
                if df.empty:
                    logger.warning(f"Sem dados para retornar para o endpoint: {self.endpoint_name}")
                    return pd.DataFrame(), None, None
                logger.info(f"Nome dos campos para apoio: {df.columns.to_list()}")
                logger.info(f"Retorno da API :{df.head(5)}")
                
                if self.field_date not in df.columns:
                    logger.error(f"A coluna '{self.field_date}' não foi encontrada no retorno de {self.endpoint_name}. Deve ser feita a correção do campo.")
                    return pd.DataFrame(), None, None

                df[self.field_date] = pd.to_datetime(
                    df[self.field_date],
                    format="%d/%m/%Y",
                    errors="coerce"
                )
                
                p1 = df[self.field_date].min()
                p2 = df[self.field_date].max()
                
                return df, p1, p2

            except ValueError: 
                logger.error(f'❌ {self.endpoint_name}: Resposta não é um JSON válido.')
                logger.error(f'Conteúdo parcial da resposta: {response.text[:5000]}')
                return pd.DataFrame(), None, None

        except r.exceptions.Timeout:
            logger.error(f'❌ Timeout: O servidor demorou demais para responder em {self.endpoint_name}.')
            return pd.DataFrame(), None, None
            
        except Exception as e:
            logger.error(f'❌ Erro inesperado em {self.endpoint_name}: {str(e)}')
            return pd.DataFrame(), None, None