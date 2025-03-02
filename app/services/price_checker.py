def check_price():
    # 適宜 `scrapers` モジュールを呼び出して処理を行う
    from scrapers.run_spider import execute_spider
    result = execute_spider()
    # 必要に応じてロジック追加
    return result