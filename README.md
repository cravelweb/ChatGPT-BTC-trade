# ChatGPT BTC trade - ビットコイン自動トレードボット

## 概要

ChatGPT BTC tradeは、ChatGPTを使って日本円とビットコインの売買を自動化するトレーディングボットです。BitFlyer APIを使用してビットコインの市場データおよびアカウントの資産情報を取得し、OpenAI APIのGPT-4oモデルを使用して売買判断を行います。また、注文の実行やキャンセルも自動で行います。

## 機能

- ビットコインの価格履歴の取得（CryptoCompare APIを使用）
- 売買判断の実施（OpenAI APIを使用）
- 現在の資産残高、オープンオーダー、取引履歴の取得（bitFlyer Lightning APIを使用）
- 売買注文の実施およびキャンセル（bitFlyer Lightning APIを使用）
- 日次のログファイル出力

## 導入方法

1. APIキーを取得します。必要なキーは以下の4種類です。

- bitFlyer Lightning APIキー
- bitFlyer Lightning APIシークレット
- OpenAI APIキー
- CryptoCompare APIキー

それぞれの取得方法は各サービスの案内等を参照してください。

2. リポジトリをクローンします。

3. 仮想環境を作成して有効化します。

    ```sh
    # 仮想環境の作成
    python -m venv venv

    # 仮想環境の有効化 (Windows)
    venv\Scripts\activate

    # 仮想環境の有効化 (Unix or MacOS)
    source venv/bin/activate
    ```

4. 必要なライブラリをインストールします。

    ```sh
    pip install -r requirements.txt
    ```

5. `.env`ファイルをプロジェクトのルートディレクトリに作成し、取得したAPIキーを記述します。

    ```
    BITFLYER_API_KEY = 'Your Bitflyer API Key'
    BITFLYER_API_SECRET = 'Your Bitflyer API Secret'
    OPENAI_API_KEY = 'Your OpenAI API Key'
    CRYPTCOMPARE_API_KEY = 'Your Cryptocompare API Key'
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

なお、メインプログラムは実行中はループ動作するようになっているため自動停止しません。
Ctrl + Cなどの強制停止などを使って適切にプログラムを停止してください。


## 注意事項

- APIキーや秘密鍵はセキュリティの観点から外部に漏れないように管理してください。
- このプログラムはChatGPTの関数呼び出しと他APIとの機能連携を学習するためのサンプルツールとして公開しています。
- このプログラムはPyhon、OpenAI API、bitFlyer Lightning APIほか機能や動作環境の十分な理解がある方の利用を想定しています。
- 実際の仮想通貨の売買の目的に使用する際にはプログラムの動作を十分に理解した上でご利用ください。
- 動作の保証のほか、このプログラムによって発生したいかなる事象に対して一切の責任を負いません。

## ライセンス

このプロジェクトはMITライセンスのもとで公開されています。詳細はLICENSEファイルをご覧ください。

