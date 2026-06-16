import os
from dotenv import load_dotenv
from loguru import logger
from modules.PipelineUpdate import PipelineUpdate
from etl_reporter_ai.logger_sender import LoggerSender

def main():
    
    load_dotenv()
    # ARQUIVO_EXCEL = r'C:\TreeSolution\Codes\[ETL] - Teknisa\input\input.xlsx' 
    ARQUIVO_EXCEL = r'D:\Tree Solution\[ETL] - Teknisa\input\input.xlsx'  
    NOME_PLANILHA = "input"
    URL_BASE_API = "https://api-zmartbi.teknisa.com"       
    emails_destino = os.getenv("TO_EMAIL", "")
    lista_emails = [email.strip() for email in emails_destino.split(",") if email.strip()]
    
    meu_logger = LoggerSender(
        pipeline_name='ETL Teknisa',
        log_file="logs/etl_checklist.log",
        to_list=lista_emails,  
        subject="Relatório ETL Teknisa"
    )
    
    meu_logger.setup_logger()
    logger.info("🚀 Iniciando a rotina principal do orquestrador ETL...")
    try:
        pipeline = PipelineUpdate(
            excel_path=ARQUIVO_EXCEL,
            url_main=URL_BASE_API,
            sheet_name=NOME_PLANILHA
        )
        
        pipeline.execute_pipeline()
        
    except Exception as e:
        logger.critical(f"❌ Falha crítica estrutural no script main: {e}")
        
    finally:
        logger.info("🏁 Encerrando rotina do script. Preparando envio de logs via e-mail...")
        meu_logger.send_log_to_email()

if __name__ == "__main__":
    main()