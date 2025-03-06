import os

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from pytz import timezone

from app.services.price_checker import check_price


def create_scheduler(app):
    """Flaskアプリにスケジューラーを紐付けて作成"""
    scheduler = BackgroundScheduler()

    # ジョブストア (スケジュールの永続化設定)
    jobstores = {
        "default": SQLAlchemyJobStore(url=f"sqlite:///{os.path.join(os.getcwd(), 'instance', 'dell_laptop.db')}")  # SQLiteにスケジュールを保存
    }
    scheduler.configure(jobstores=jobstores)

    # タスクの登録: 1日おきに実行 (午前0時)
    scheduler.add_job(
        func=check_price,  # 実行する関数
        trigger="cron",  # cron形式
        hour=8, minute=00,  # 毎日午前8時
        id="daily_price_check",  # タスクID
        replace_existing=True,  # 同じIDのタスクを置き換える
        timezone=timezone('Asia/Tokyo')
    )

    # Flaskアプリが停止する際にスケジューラーもシャットダウン
    if not scheduler.running:
        # scheduler.start()
        app.logger.info("スケジューラーが開始されました。")
    return scheduler
