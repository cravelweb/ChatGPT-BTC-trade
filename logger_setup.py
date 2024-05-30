import logging
import os
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

# ログディレクトリの作成
log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# ログフォーマットの設定
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# ログファイルハンドラーの設定
log_file = os.path.join(log_dir, f'trading_{datetime.now().strftime("%Y%m%d")}.log')
file_handler = TimedRotatingFileHandler(log_file, when='midnight', interval=1, backupCount=7, encoding='utf-8')
file_handler.suffix = "%Y%m%d"
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)

# コンソールハンドラーの設定
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.INFO)

# ルートロガーの設定
logging.basicConfig(level=logging.INFO, handlers=[file_handler, console_handler])

# ロガーの取得関数
def get_logger(name):
    return logging.getLogger(name)
