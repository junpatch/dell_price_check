import logging
import os
import subprocess

from main import app

DEFAULT_SPIDER = 'laptop'  # デフォルトのスパイダー名を定義
ENCODING = 'utf-8'  # エンコーディング


def build_scrapy_command(spider_name):
    """Scrapyコマンドを構築"""
    return f"scrapy crawl {spider_name}"


def handle_process_output(process):
    """プロセスの結果を処理"""
    if process.returncode != 0:
        error_message = (
            f"スパイダーの実行に失敗しました:\n"
            f"標準出力: {process.stdout}\n"
            f"標準エラー: {process.stderr}"
        )
        raise RuntimeError(error_message)
    return {"success": True, "message": "スパイダーの実行が成功しました", "stdout": process.stdout, "stderr": process.stderr}


def execute_spider(spider_name=DEFAULT_SPIDER):
    """
    Scrapyスパイダーをサブプロセスで実行

    :param spider_name: 実行するスパイダーの名前（デフォルトは 'laptop'）。
    """
    # 作業ディレクトリを取得（scrapersを指定）
    project_dir = os.path.abspath(os.path.dirname(__file__))
    command = build_scrapy_command(spider_name)

    app.logger.info(f"project_dir: {project_dir}")

    try:
        # コマンドを実行
        app.logger.info(f"Spider executed: {command}")

        process = subprocess.Popen(
            command, cwd=project_dir, shell=True
        )
        # 結果処理
        process.wait()  # プロセスが終了するまで待つ
        # process_status["status"] = "Completed"  # 終了後、ステータスを更新

        app.logger.info(f"Spider result: {process.returncode}")
        return handle_process_output(process)
    except Exception as e:
        print(f"Spider実行エラー発生: {e}")
        raise
