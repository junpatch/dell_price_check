import requests
# from settings import LINE_CHANNEL_TOKEN

#
# class LineNotifier:
#     def send_notifications(self, price_changes):
#         headers = {
#             "Content_Type": "application/json",
#             "Authorization": "Bearer " + 'YOUR_CHANNEL_ACCESS_TOKEN'
#         }
#
#         message = (
#             f"🚨価格変動のお知らせ🚨\n"
#             f"商品名: {change['name']}\n"
#             f"旧価格: ¥{change['old_price']}\n"
#             f"新価格: ¥{change['new_price']}\n"
#             f"商品リンク: {change['url']}"
#         )
#         requests.post(
#             "https://api.line.me/v2/bot/message/push",
#             headers=headers,
#             data={"to":user_id,"message": message}
#         )
#
#     def send_notification(self, param):
#         pass
class LineNotifier:
    def send_notifications(self, old_price, new_price, name, url):
        YOUR_CHANNEL_ACCESS_TOKEN='eyJhbGciOiJIUzI1NiJ9.GrG84oMSZMOey3DAe-_U-XszQQmMRuv0d_yx8emPvTlrn66R3TweMkbudFnh-1-1lAWv_i2Gv95wfdDqcd9e2l2touJOZvqBCPVI6wNGok9J9HjgNRRIL-qtY3coXu0K.OxFBZ2xvuFnHL0yKQJrK3Iajv7XPoUIQRxDMp1DGJVs'

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {YOUR_CHANNEL_ACCESS_TOKEN}"
        }

        message = (
            f"🚨価格変動のお知らせ🚨\n"
            f"商品名: {name}\n"
            f"旧価格: {old_price}¥\n"
            f"新価格: {new_price}¥\n"
            f"商品リンク: {url}"
        )

        payload = {
            "to": "Ua34ec613cf697020668168a77bf6efad",  # メッセージを送るユーザーID（またはグループID）
            "messages": [
                {
                    "type": "text",
                    "text": message
                }
            ]
        }

        res=requests.post(
            "https://api.line.me/v2/bot/message/push",
            headers=headers,
            json=payload
        )


        print(f"ステータスコード: {res.status_code}")
        print(res.json())

# res = requests.get(
#     "https://api.line.me/oauth2/v2.1/verify",
#     headers={"Content-Type": "application/x-www-form-urlencoded"},
#     params={
#         "access_token": "eyJhbGciOiJIUzI1NiJ9.GrG84oMSZMOey3DAe-_U-XszQQmMRuv0d_yx8emPvTlrn66R3TweMkbudFnh-1-1lAWv_i2Gv95wfdDqcd9e2l2touJOZvqBCPVI6wNGok9J9HjgNRRIL-qtY3coXu0K.OxFBZ2xvuFnHL0yKQJrK3Iajv7XPoUIQRxDMp1DGJVs"
#     }
# )
# print(f"ステータスコード: {res.status_code}")
# print(res.json())