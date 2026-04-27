import pandas as pd
from urllib.parse import quote_plus
from createConnectionString import create_connection
from sqlalchemy import text, inspect, DateTime, String # <-- Adicionado String aqui
from datetime import datetime
import os
import logging

def save(df: pd.DataFrame, table: str, coluna_filtro: str, p1: str, p2: str) -> None:
    if not df.empty:



        for col in df.columns:
            if col != coluna_filtro:
                df[col] = df[col].apply(lambda x: str(x) if pd.notnull(x) else None)

        DB_SERVER = os.getenv("DB_SERVER")
        DB_DATABASE = os.getenv("DB_DATABASE")
        DRIVER = os.getenv("DRIVER")
        
        odbc_params = quote_plus(
            f"DRIVER={{{DRIVER}}};"
            f"SERVER={DB_SERVER};"
            f"DATABASE={DB_DATABASE};"
            "UID=robo_vmarket;"
            "PWD=robo123;"
        )
        engine = create_connection(odbc_params)
        
        inspector = inspect(engine)
        
        if inspector.has_table(table):
            print(f"ℹ️ Tabela '{table}' encontrada. Verificando dados antigos...")
            logging.info(f"ℹ️ Tabela '{table}' encontrada. Verificando dados antigos...")
            
            colunas_no_banco = [col['name'] for col in inspector.get_columns(table)]
    
            colunas_sobrando = set(df.columns) - set(colunas_no_banco)
            
            if colunas_sobrando:
                df = df.drop(columns=list(colunas_sobrando))
            
            try:
                with engine.connect() as conn:
                    sql_delete = text(f"""
                                DELETE FROM {table}
                                WHERE {coluna_filtro} >= :inicio
                                AND {coluna_filtro} <= :fim
                                    """)
                    msg =f"🔄 Apagando dados de {p1} até {p2} da tabela {table}..."
                    print(msg)
                    logging.info(msg)
                    result = conn.execute(sql_delete, {    
                                              "inicio": p1,  
                                                "fim": p2
                                            }
                                )
                    conn.commit()
                    print(f"🗑️ {result.rowcount} registros apagados com sucesso.")
                    logging.info(f"🗑️ {result.rowcount} registros apagados com sucesso.")
            except Exception as e:
                logging.error(f"Erro ao tentar apagar dados antigos: {e}")
                print(f"Erro ao tentar apagar dados antigos: {e}")
        else:
            print(f"🆕 Tabela '{table}' não existe. Ela será criada agora.")
            logging.info(f"🆕 Tabela '{table}' não existe. Ela será criada agora.")


        mapeamento_tipos = {col: String() for col in df.columns if col != coluna_filtro}
        mapeamento_tipos[coluna_filtro] = DateTime()

        df.to_sql(name=table, con=engine, if_exists='append', index=False, chunksize=1000, 
            dtype=mapeamento_tipos) 
            
        num_rows = len(df)
        logging.info(f"📤 {num_rows} inseridos com sucesso na tabela {table}!")
        print(f"📤 {num_rows} inseridos com sucesso na tabela {table}!")
        
    else:
        logging.warning('⚠️ Sem dados para inserir..')
        print('⚠️ Sem dados para inserir..')