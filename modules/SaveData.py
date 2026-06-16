import pandas as pd
from urllib.parse import quote_plus
from sqlalchemy import text, inspect, DateTime, String, create_engine
import os
from loguru import logger

class SaveData:
    def __init__(
        self,
        df: pd.DataFrame,
        name_table: str,
        field_filter: str,
        period_min: str,
        period_max: str
    ):
        self.df = df
        self.name_table = name_table
        self.field_filter = field_filter
        self.period_min = period_min
        self.period_max = period_max
        self.odbc_params = quote_plus(
            f"DRIVER={{{os.getenv('DRIVER')}}};"
            f"SERVER={os.getenv('DB_SERVER')};"
            f"DATABASE={os.getenv('DB_DATABASE')};"
            f"Trusted_Connection=yes;"
            f"TrustServerCertificate=yes;"  
        )
        
    def _create_connection(self):
        connection_string = f"mssql+pyodbc:///?odbc_connect={self.odbc_params}"
        logger.info("🔄 Conectando ao banco de dados...")
        try:
            engine = create_engine(connection_string)
            with engine.connect() as conn:
                pass
            logger.success("Conexão com o banco realizada com sucesso!")
            return engine
        
        except Exception as e:
            logger.error(f"❌ Ocorreu um erro ao criar a conexão com o banco de dados: {e}")
            return None

    def save(self) -> None:
        engine = self._create_connection()
        if not engine:
            logger.error("A carga foi abortada porque a conexão com o banco falhou.")
            return

        for col in self.df.columns:
            if col != self.field_filter:
                self.df[col] = self.df[col].apply(lambda x: str(x) if pd.notnull(x) else None)
            
        inspector = inspect(engine)
        mapeamento_tipos = None
            
        if inspector.has_table(self.name_table):
            logger.info(f"ℹ️ Tabela '{self.name_table}' encontrada. Verificando estrutura e dados antigos...")
            
            colunas_no_banco = [col['name'] for col in inspector.get_columns(self.name_table)]
            
            colunas_sobrando = set(self.df.columns) - set(colunas_no_banco)
            if colunas_sobrando:
                logger.warning(f"Ignorando colunas novas que não existem no banco: {colunas_sobrando}")
                self.df = self.df.drop(columns=list(colunas_sobrando))
            
            try:
                with engine.connect() as conn:
                    with conn.begin():
                        sql_delete = text(f"""
                            DELETE FROM {self.name_table}
                            WHERE {self.field_filter} >= :inicio
                            AND {self.field_filter} <= :fim
                        """)
                        logger.info(f"🔄 Apagando dados de {self.period_min} até {self.period_max} da tabela {self.name_table}...")
                        
                        result = conn.execute(sql_delete, {    
                            "inicio": self.period_min,  
                            "fim": self.period_max
                        })
                        logger.success(f"🗑️ {result.rowcount} registros apagados com sucesso.")
            except Exception as e:
                logger.error(f"Erro ao tentar apagar dados antigos: {e}")
                return 

        else:
            logger.info(f"🆕 Tabela '{self.name_table}' não existe. Ela será criada agora.")
            mapeamento_tipos = {col: String() for col in self.df.columns if col != self.field_filter}
            mapeamento_tipos[self.field_filter] = DateTime()

        try:
            logger.info(f"⏳ Inserindo dados na tabela {self.name_table}...")
            
            to_sql_kwargs = {
                "name": self.name_table,
                "con": engine,
                "if_exists": 'append',
                "index": False,
                "chunksize": 1000
            }
            if mapeamento_tipos:
                to_sql_kwargs["dtype"] = mapeamento_tipos

            self.df.to_sql(**to_sql_kwargs) 
                
            num_rows = len(self.df)
            logger.success(f"📤 {num_rows} registros inseridos com sucesso na tabela {self.name_table}!")
        except Exception as e:
            logger.error(f"❌ Erro ao inserir os dados: {e}")