import psycopg2
from core.config import DB_CONFIG

print("--- НАЧАЛО ДИАГНОСТИКИ БД ---")
print(f"1. Пробую подключиться к: {DB_CONFIG['host']}:{DB_CONFIG['port']} (БД: {DB_CONFIG['database']})...")

try:
    # Пытаемся подключиться
    conn = psycopg2.connect(**DB_CONFIG)
    print("✅ УСПЕХ: Соединение с PostgreSQL установлено!")

    # Создаем курсор для команд
    cur = conn.cursor()

    # 2. Проверяем, какие таблицы есть внутри
    print("\n2. Проверяю список таблиц...")
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public';
    """)

    tables = cur.fetchall()

    if tables:
        print(f"✅ Найдены таблицы ({len(tables)} шт.):")
        for t in tables:
            print(f"   - {t[0]}")

        # 3. Пробуем посчитать записи в главной таблице (если она есть)
        target_table = "biorefinery_data_clean"
        found = False
        for t in tables:
            if t[0] == target_table:
                found = True
                break

        if found:
            cur.execute(f'SELECT COUNT(*) FROM "{target_table}"')
            count = cur.fetchone()[0]
            print(f"\n✅ Таблица '{target_table}' найдена. В ней {count} строк.")
        else:
            print(f"\n⚠️ ВНИМАНИЕ: Таблица '{target_table}' НЕ найдена в базе!")
            print("Возможно, она называется по-другому? Проверь список выше.")

    else:
        print("⚠️ База данных пустая (нет таблиц).")

    cur.close()
    conn.close()

except psycopg2.OperationalError as e:
    print("\n❌ ОШИБКА ПОДКЛЮЧЕНИЯ (OperationalError):")
    print("Python не может достучаться до сервера.")
    print(f"Детали: {e}")
    print("\nЧТО ПРОВЕРИТЬ:")
    print("1. Запущен ли PostgreSQL? (Службы Windows)")
    print(f"2. Верный ли порт? У тебя указан {DB_CONFIG.get('port')}, а стандартный - 5432.")
    print("3. Верный ли пароль в config.py?")

except Exception as e:
    print(f"\n❌ ДРУГАЯ ОШИБКА: {e}")

print("\n--- КОНЕЦ ДИАГНОСТИКИ ---")