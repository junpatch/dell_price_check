# Dell Laptop Price Tracker
## 概要
このプロジェクトは、DellのノートPCの価格データを収集し、データベースに保存するためのWebスクレイピングツールです。さらに、価格が変更された場合には通知を送信する機能を提供します。
### 主な機能
- **価格データのスクレイピング**: 商品情報や価格履歴をデータベースに格納。
- **価格変動通知**: 価格が変更されたらLINEに通知を送信。
- **SQLiteを使用したローカルデータベースの構築と保存**。
- **GitHub Actionsを使用した定期実行**: 定期的にスクレイピングを実行可能。

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
1. **環境変数を設定します:**

このプロジェクトでは、環境変数を `.env` ファイルに記述することを推奨します。
### `.env` ファイルの作成
1. プロジェクトのルートフォルダに `.env` ファイルを作成します。
``` bash
   touch .env
```
1. 以下の内容を `.env` に記述します。
``` 
   LINE_ACCESS_TOKEN=あなたのLINEアクセストークン
```
1. Pythonアプリケーションで環境変数を読み込むため、`python-dotenv` ライブラリを使用しています。`requirements.txt` に含まれているため、手動で追加インストールする必要はありません。

## 使い方
### 1. `main.py` を直接実行する場合:
以下のコマンドを使用して、スクレイピングと通知機能を実行します。
``` bash
python main.py
```
### 2. GitHub Actionsを使用した定期実行:
### **GitHub Actions の設定手順**
このプロジェクトでは、`python-app.yml` を使ってGitHub Actionsでスケジュールされたジョブを実行します。
#### 1. **ワークフローファイルの内容**
`python-app.yml`の内容は以下の通りです:
``` yaml
name: Python application

on:
  schedule:
    - cron: '0 0 * * *'  # 毎日午前0時 (UTC) に実行
  workflow_dispatch:       # 手動実行も可能

env:
  LINE_ACCESS_TOKEN: ${{ secrets.LINE_ACCESS_TOKEN }}
  GIT_USER_NAME: ${{ secrets.GIT_USER_NAME }}
  GIT_USER_EMAIL: ${{ secrets.GIT_USER_EMAIL }}
  GH_PERSONAL_ACCESS_TOKEN: ${{ secrets.GH_PERSONAL_ACCESS_TOKEN }}

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python 3.8
      uses: actions/setup-python@v3
      with:
        python-version: "3.8"

    - name: Chrome setup
      run: |
        sudo apt-get update
        sudo apt-get install -y unzip wget
        sudo apt-get install -y google-chrome-stable

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install chromedriver-autoinstaller
        pip install -r requirements.txt
    
    - name: Check installed versions
      run: |
        google-chrome --version
        chromedriver --version
    
    - name: Run main.py
      run: |
        python main.py
    
    - name: Commit changes
      run: |
        git config user.name "${GIT_USER_NAME}"
        git config user.email "${GIT_USER_EMAIL}"
        git remote set-url origin https://${GIT_USER_NAME}:${GH_PERSONAL_ACCESS_TOKEN}@github.com/junpatch/dell_price_check.git
        git remote -v
        git add .
        git commit -m "Scheduled Run"
    
    - name: Push changes
      run: |
        git push origin main
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```
上記のワークフローは、以下の処理を行います:
1. Python環境のセットアップと依存関係のインストール
2. Google ChromeとChromeDriverのセットアップ
3. `main.py` の実行
4. ファイルの更新内容をGitHubにコミット、プッシュ

#### 2. **必要な環境変数とその設定**
このワークフローで使用する主要な環境変数を以下に示します:

| 環境変数名 | 意味 | 設定箇所 |
| --- | --- | --- |
| `LINE_ACCESS_TOKEN` | LINE通知に使用するアクセストークン | GitHub Secrets |
| `GIT_USER_NAME` | リポジトリへの変更をコミットするユーザー名 | GitHub Secrets |
| `GIT_USER_EMAIL` | リポジトリへの変更をコミットするユーザーのメール | GitHub Secrets |
| `GH_PERSONAL_ACCESS_TOKEN` | GitHubリポジトリへのアクセスに使用するトークン | GitHub Secrets |
##### **GitHubでの環境設定**
コマンド実行後、 `Settings > Secrets and variables > Actions` ページで以下の手順を行なってください:
1. **Secretsの追加**
    1. レポジトリ設定ページに移動します。
    2. サイドバーから `Secrets and variables` > `Actions` > `New repository secret` を選択します。
    3. 下記を追加してください:
        - **`LINE_ACCESS_TOKEN`**: LINE通知に利用するアクセストークン
        - **`GIT_USER_NAME`**: GitHubのユーザー名
        - **`GIT_USER_EMAIL`**: GitHub登録メールアドレス
        - **`GH_PERSONAL_ACCESS_TOKEN`**: GitHub Personal Access Token（適切な権限が付与されている必要あり）

2. **設定後の動作確認** 設定が完了すれば、手動で `Actions` タブを開き、`Run workflow` をクリックすることで手動実行が可能です。また、スケジュールに従って自動実行されます。

### 補足
- **スケジュール設定**: 現状では毎日午前0時 (UTC) にジョブを実行する設定です。実行タイミングの変更は、`cron` 設定値を変更して行います。
- **エラー時対応**: 実行中にエラーが発生した場合は`Actions`ログで詳細を確認してください。
- **リポジトリ更新の自動化**: スケジュール実行時に変更内容をリポジトリに自動でプッシュするプロセスが含まれています。


## ファイル構造
``` 
.
├── main.py         # メインエントリポイント: スクレイピング/通知機能実行
├── pipelines.py    # SQLAlchemyベースのPipeline (価格データの保存を担当)
├── model/
│   ├── models.py   # データベース構造（SQLAlchemyモデル）
├── notification/
│   ├── line_notifier.py  # 通知クラス (価格変更時に通知)
├── .env            # 環境変数を記載したファイル
├── .github/
│   ├── workflows/
│       ├── schedule.yml  # GitHub Actions定期実行ワークフロー
├── requirements.txt # Python依存ライブラリリスト
└── README.md       # このファイル
```
## 環境変数の利用
- プロジェクトでは、`LINE_ACCESS_TOKEN` (LINE通知用のアクセストークン) を `.env` ファイルで管理します。
- アプリケーション起動時、`.env` ファイルに記述されたキーを自動的に読み取ります。

## 依存ライブラリ
`requirements.txt` の中には、以下の主要な依存ライブラリが含まれています:
- **Scrapy** - Webスクレイピングフレームワーク
- **SQLAlchemy** - データベース処理用ORM
- **itemadapter** - Scrapyとデータ変換の連携を管理
- **python-dotenv** - `.env` ファイルから環境変数を読み込むためのライブラリ

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
