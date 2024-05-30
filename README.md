# ChatGPT BTC trade - GPT4 ビットコイン自動トレードボット

## 概要

ChatGPT BTC tradeは、ChatGPTを使って日本円とビットコインの売買を自動化するトレーディングボットです。BitFlyer APIを使用してビットコインの市場データおよびアカウントの資産情報を取得し、OpenAI APIのGPT-4oモデルを使用して売買判断を行います。また、注文の実行やキャンセルも自動で行います。

## 機能

- ビットコインの価格履歴の取得
- 売買判断の実施（OpenAI APIを使用）
- 売買注文の実施およびキャンセル
- 現在の資産残高、オープンオーダー、取引履歴の取得
- 日次のログファイル出力

## 導入方法

1. リポジトリをクローンします。

2. 仮想環境を作成して有効化します。

    ```sh
    # 仮想環境の作成
    python -m venv venv

    # 仮想環境の有効化 (Windows)
    venv\Scripts\activate

    # 仮想環境の有効化 (Unix or MacOS)
    source venv/bin/activate
    ```

3. 必要なライブラリをインストールします。

    ```sh
    pip install -r requirements.txt
    ```

4. `.env`ファイルをプロジェクトのルートディレクトリに作成し、以下のようにBitFlyer APIキーとOpenAI APIキーを設定します。

    ```
    BITFLYER_API_KEY=your_bitflyer_api_key
    BITFLYER_API_SECRET=your_bitflyer_api_secret
    OPENAI_CRYPT_API_KEY=your_openai_api_key
    ```

## 実行方法

1. 以下のコマンドを使用してPythonスクリプトを実行します。

    ```sh
    # 仮想環境を有効化 (必要に応じて)
    venv\Scripts\activate  # Windows
    source venv/bin/activate  # Unix or MacOS

    # Pythonスクリプトの実行
    python main.py
    ```

## ディレクトリ構成

bitcoin-trading-bot/
├── logs/ # ログファイルディレクトリ
├── .env # 環境変数ファイル
├── main.py # メインスクリプト
├── bitflyer_client.py # BitFlyer APIクライアント
├── price_history.py # 価格履歴モジュール
├── trading.py # トレードモジュール
├── portfolio.py # ポートフォリオモジュール
├── execution_history.py# 約定履歴モジュール
├── order_book.py # 注文板モジュール
├── trading_decision.py # 売買判断モジュール
├── logger_setup.py # ロガー設定モジュール
└── requirements.txt # 依存関係ファイル


## 注意事項

- このプロジェクトは学習目的であり、実際の取引で使用する際には十分な注意が必要です。
- APIキーや秘密鍵はセキュリティの観点から外部に漏れないように管理してください。

## ライセンス

このプロジェクトはMITライセンスのもとで公開されています。詳細はLICENSEファイルをご覧ください。

