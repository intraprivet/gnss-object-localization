gnss-object-localization/
│
├── main.py             # Главный pipeline (RTK, автораспаковка, запуск, анализ)
├── config.py           # Python-конфиг с путями к файлам, настройками pipeline
├── README.md           # Документация, цели, структура, инструкции
│
├── config/
│   └── kinematic.conf  # Файл настроек RTKLIB (режим Kinematic, auto-update путей)
│
├── gnss_data/
│   └── 017_GRAZ/
│         ├── GRAZ00AUT_R_20250170000_01D_30S_MO.crx.gz     # Твои данные (ровер+база)
│         ├── GRAZ00AUT_R_20250170000_01D_30S_MO.crx        # (автоматически появляется после распаковки)
│
├── outdata/
│   └── solution.pos    # RTKLIB результат (.pos-файл)
│
└── __pycache__/        # (создаётся автоматически, игнорируется)
# gnss-object-localization