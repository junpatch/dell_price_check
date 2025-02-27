# Dell Laptop Price Tracker
## 概要
このプロジェクトは、DellのノートPCの価格データを収集し、データベースに保存するためのWebスクレイピングツールです。 さらに、価格が変更された場合には通知を送信する機能を提供します。
### 主な機能
- **価格データのスクレイピング**: 商品情報や価格履歴をデータベースに格納。
- **価格変動通知**: 価格が変更されたら指定のチャンネルに通知を送信。
- **SQLiteを使用したローカルデータベースの構築と保存**。

## 必要な環境
### 使用技術
- **Python 3.8以降**
- **Scrapy**
- **SQLAlchemy**
- **SQLite**

## インストール
1. **リポジトリをクローンします:**
``` bash
git clone https://github.com/yourusername/dell-laptop-price-tracker.git
cd dell-laptop-price-tracker
```
1. **必要なライブラリをインストールします:**
``` bash
pip install -r requirements.txt
```
1. **データベースを初期化します:**
``` bash
python -c "from model import models; models.Base.metadata.create_all()"
```
## ファイル構造
``` 
.
├── main.py         # メインエントリポイント（必要に応じて）
├── pipelines.py    # SQLAlchemyベースのPipeline (価格データの保存を担当)
├── model/
│   ├── models.py   # データベース構造（SQLAlchemyモデル）
├── notification/
│   ├── line_notifier.py  # 通知クラス (価格変更時に通知)
├── scrapy_spider/
│   └── ...         # スパイダー関連のコード
├── requirements.txt # Python依存ライブラリリスト
└── README.md       # このファイル
```
## 使い方
1. **Scrapyスパイダーを実行して価格データを収集します:**
``` bash
scrapy crawl dell_laptop_spider
```
1. **商品情報と価格履歴がSQLiteデータベースに保存されます。**
2. **価格が変更された場合は通知が送信されます（例: LINE通知）。**

## カスタマイズ方法
### データベース設定
- データベースの接続URL (`DATABASE_URL`) は、`pipelines.py` 内で設定されています。
- SQLite以外のデータベース（例: PostgreSQL, MySQL）にも簡単に変更可能です。
``` python
DATABASE_URL = 'sqlite:///dell_laptop.db'
```
### 通知設定
- `notification/line_notifier.py` を編集し、通知方法をカスタマイズできます。
- 現在はLINE通知に対応していますが、APIキーやWebhookなどを編集することで他の通知システムに対応可能です。

## 依存ライブラリ
`requirements.txt` の中には、以下の主要な依存ライブラリが含まれています:
- **Scrapy** - Webスクレイピングフレームワーク
- **SQLAlchemy** - データベース処理用ORM
- **itemadapter** - Scrapyとデータ変換の連携を管理

インストールは以下のコマンドで実行できます:
``` bash
pip install -r requirements.txt
```
## 今後の改善点
- より詳細なエラーログの追加。
- PostgreSQLやMySQLなど、SQLite以外のデータベースサポート。
- 他の通知サービス対応（例: Slack、メール通知など）。
- テストコードの追加と完全なユニットテストの実装。

## 貢献
1. このリポジトリをフォークします。
2. 新しいブランチを作成します (例: `feature-add-notification`):
``` bash
   git checkout -b feature-add-notification
```
1. 修正をコミットします:
``` bash
   git commit -m 'Add new notification feature'
```
1. プルリクエストを送信します。

## ライセンス
このプロジェクトは [MIT License](LICENSE) の元で提供されています。
