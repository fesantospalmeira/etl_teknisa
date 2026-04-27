import requests as r
import pandas as pd
import logging
import saveData
import time

def get_data(url:str, nome_endpoint:str, headers:dict, campo_data:str) -> None:
    try:
        response = r.get(url=url, headers=headers, timeout=300) 
        
        if response.status_code != 200:
            logging.error(f'❌ Erro HTTP {response.status_code} em {nome_endpoint}')
            logging.error(f'❌ {response.text[:100]}')
            return
        try:
            data = response.json()
            
            if not data:
                msg = f'⚠️ {nome_endpoint}: API retornou lista vazia.'
                
                logging.warning(msg)
                logging.warning(msg)
                return

            df = pd.DataFrame(data)
            
            df[campo_data] = pd.to_datetime(
                df[campo_data],
                format="%d/%m/%Y",
                errors="coerce"
        )
            p1 = df[campo_data].min()
            p2 = df[campo_data].max()
            
            saveData.save(df, nome_endpoint, campo_data, p1, p2)
            time.sleep(2) 

        except ValueError: 
            logging.error(f'❌ {nome_endpoint}: Resposta não é um JSON válido.')
            logging.error(f'Conteúdo parcial da resposta: {response.text[:5000]}')

    except r.exceptions.Timeout:
        logging.error(f'❌ Timeout: O servidor demorou demais para responder em {nome_endpoint}. Erro: {response.status_code}')
    except Exception as e:
        logging.error(f'❌ Erro {response.status_code} inesperado em {nome_endpoint}: {str(e)}')