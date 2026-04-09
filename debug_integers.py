import pandas as pd
import re


def check_data():
    print("🕵️‍♂️ ЗАПУСК ДЕТЕКТИВА: Ищем числа-убийцы...")

    file_path = "data/merged_documents.xlsx"
    df = pd.read_excel(file_path, engine='openpyxl')

    # 1. Маппинг (как в основном скрипте)
    rename_map = {
        'Год': 'publication_year',
        'TRL': 'trl_level'
    }
    df = df.rename(columns=rename_map)

    print(f"Всего строк: {len(df)}")
    print("-" * 30)

    # --- ПРОВЕРКА ГОДА ---
    print("🔍 Анализ колонки 'publication_year'...")
    bad_years = []

    for index, row in df.iterrows():
        val = row.get('publication_year')

        # Пытаемся превратить в число
        try:
            if pd.isna(val): continue

            # Чистим так же, как планировали
            text = str(val).strip()
            match = re.search(r'\b(18|19|20)\d{2}\b', text)

            if match:
                num = int(match.group())
            else:
                # Если регулярка не нашла, пробуем тупо int()
                # Именно здесь может вылезти гигантское число
                try:
                    num = int(float(val))
                except:
                    continue  # Не число - не проблема для integer overflow (упадет раньше)

            # ПРОВЕРКА НА ЛИМИТ POSTGRES (2 147 483 647)
            if num > 2147483647 or num < -2147483648:
                bad_years.append((index + 2, val))  # +2 т.к. в Excel заголовки

        except Exception as e:
            pass

    if bad_years:
        print(f"❌ НАЙДЕНО {len(bad_years)} ОШИБОК В ГОДАХ!")
        for idx, val in bad_years[:5]:
            print(f"   Строка Excel {idx}: Значение = '{val}'")
    else:
        print("✅ Годы чистые (нет переполнения).")

    print("-" * 30)

    # --- ПРОВЕРКА TRL ---
    print("🔍 Анализ колонки 'trl_level'...")
    bad_trls = []

    for index, row in df.iterrows():
        val = row.get('trl_level')
        try:
            if pd.isna(val): continue

            # Эмуляция "глупой" конвертации, которая может ломать базу
            try:
                num = int(float(val))
                # Если число больше 9 (наш предел TRL), это подозрительно
                # Но ошибка базы возникает только если > 2 млрд
                if num > 2147483647:
                    bad_trls.append((index + 2, val))
            except:
                pass
        except:
            pass

    if bad_trls:
        print(f"❌ НАЙДЕНО {len(bad_trls)} КРИТИЧЕСКИХ ОШИБОК В TRL!")
        for idx, val in bad_trls[:5]:
            print(f"   Строка Excel {idx}: Значение = '{val}'")
    else:
        print("✅ TRL чистые (нет переполнения).")


if __name__ == "__main__":
    check_data()