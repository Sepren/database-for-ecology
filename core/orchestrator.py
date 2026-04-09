from database.connector import DBConnector


class Orchestrator:
    def __init__(self):
        self.db = DBConnector()
        # self.analyst = AnalystAgent() <--- УБИРАЕМ, он тут не нужен

    def run_pipeline(self):
        # Просто достаем ГОТОВЫЕ данные из базы
        df = self.db.fetch_all("biorefinery_data_clean")

        # Возвращаем как есть, без повторной обработки
        return df, {"count": len(df)}