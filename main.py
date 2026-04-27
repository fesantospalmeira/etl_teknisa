import getDataApi
from dotenv import load_dotenv
from datetime import datetime,date
from SendLogEmail import send_log_email as eml
import pandas as pd
import logging
import os
import time

load_dotenv()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(BASE_DIR, "app.log")
logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    filemode="w",
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)
def main():
    url_geral = 'https://api-zmartbi.teknisa.com'
    excel_path = r'D:\Tree Solution\Teknisa\[ETL] - Teknisa\input\input.xlsx'
    # excel_path = r'C:\TreeSolution\Codes\[ETL] - Teknisa\input\input.xlsx'
    df = pd.read_excel(excel_path,sheet_name='input')
    
    for index,row in df.iterrows():
        print(" ")
        nome_endpoint = row['nome_tabela']
        webtoken = row['api_key']
        campo_data = row['campo_dt']

        headers = {
                'Content-Type': 'application/json',
                'Webtoken': webtoken
            }
        getDataApi.get_data(url_geral,nome_endpoint,headers,campo_data)
        time.sleep(3)

 
    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    TO_EMAIL = os.getenv("TO_EMAIL")

    if EMAIL_USER and EMAIL_PASSWORD and TO_EMAIL:
        eml(
            smtp_server="smtp.gmail.com",
            smtp_port=465,
            email_user=EMAIL_USER,
            email_password=EMAIL_PASSWORD,
            log_file=log_path
        )
    else:
        logging.warning("⚠️ Variáveis de email não configuradas no .env, log não enviado.")


if __name__ == '__main__':
    main()
