from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
import pandas as pd

# WebDriverのインスタンスを作成
driver = webdriver.Chrome() # あなたが使用しているブラウザに応じて変更します（Chrome, Firefox等）

# 最初のページを開く
url = "https://www.torecolo.jp/shop/goods/search.aspx?ct2=1074&p=1&filtercode13=1&ps=50&seq=nd&search=x%2csearch"
driver.get(url)

# 商品URLを保存するためのリスト
product_urls = []

while True:
    # 現在のページの全商品を取得
    items = driver.find_elements(By.CLASS_NAME, "js-enhanced-ecommerce-goods-name") # 商品のURLを含むHTML要素を特定するためのクラス名

    for item in items:
        # 商品のURLを取得
        url = item.get_attribute("href")
        
        # URLをリストに保存
        product_urls.append(url)

    try:
        # 次のページへのリンクを取得
        next_link = driver.find_element(By.LINK_TEXT, "次") # "次へ"のリンクを特定する

        # 次のページに移動
        next_link.click()

        # ページが読み込まれるまで待つ
        time.sleep(2)
    except NoSuchElementException:
        # "次へ"のリンクが見つからなければループを抜ける
        break

# WebDriverを閉じる
driver.quit()

#商品URL一覧をcsvとして出力する
import pandas as pd
df = pd.DataFrame(product_urls)
df.to_csv('product_urls.csv', index=False, header=False)


# 商品URLを出力
for url in product_urls:
    print(url)
