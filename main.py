import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from tqdm import tqdm

# 商品URLを取得する関数
def get_product_urls(driver):
    url = "https://www.torecolo.jp/shop/goods/search.aspx?ct2=1074&p=1&filtercode13=1&ps=50&seq=nd&search=x%2csearch"
    driver.get(url)

    product_urls = []

    while True:
        items = driver.find_elements(By.CLASS_NAME, "js-enhanced-ecommerce-goods-name")

        for item in items:
            url = item.get_attribute("href")
            product_urls.append(url)

        try:
            next_link = driver.find_element(By.CSS_SELECTOR, ".pager-next a")
            next_link = next_link.get_attribute("href")
            driver.get(next_link)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "js-enhanced-ecommerce-goods-name")))
        except NoSuchElementException:
            break

    return product_urls

# 商品情報を取得する関数
def get_product_info(driver, url):
    driver.get(url)
    product_name = driver.find_element(By.CLASS_NAME, "js-enhanced-ecommerce-goods-name").text
    print(product_name+"の情報を取得しています。")
    product_price = driver.find_element(By.CLASS_NAME, "js-enhanced-ecommerce-goods-price").text
    product_rarity = driver.find_element(By.ID, "spec_rarity").text
    product_code = driver.find_element(By.ID, "spec_goods").text
    product_series = driver.find_element(By.ID, "spec_release_dt").text
    card_type = driver.find_element(By.XPATH, "//dt[text()='カード種類：']/following-sibling::dd").text
    regulation = driver.find_element(By.XPATH, "//dt[text()='レギュレーション：']/following-sibling::dd").text

    result = [product_name, product_price, product_rarity, product_code, product_series, card_type, regulation]

    return result

# WebDriverの初期化
driver = webdriver.Safari()
driver.maximize_window()

try:
    # product_urls.csvを読み込む、項目名は商品URL
    df = pd.read_csv('product_urls.csv', names=['商品URL'])
    print("product_urls.csvが存在します。")
except FileNotFoundError:
    print("product_urls.csvが存在しません。")
    print("product_urls.csvを作成します。")
    product_urls = get_product_urls(driver)
    df = pd.DataFrame(product_urls)
    df.to_csv('product_urls.csv', index=False, header=False)

try:
    products = []

    # 途中から再開するためのフラグを設定
    resume_flag = False

    # 進捗状況を表示するためのtqdmを作成
    pbar = tqdm(total=len(df['商品URL']))

    # tqdmで進捗状況を表示しながらループを実行
    for url in df['商品URL']:
        # レジュームフラグがFalseであれば通常の処理を実行
        if not resume_flag:
            try:
                result = get_product_info(driver, url)
                products.append(result)
            except Exception as e:
                traceback.print_exc()
                print(f"エラーが発生しました: {e}")
                print("途中経過を保存して終了します。")
                # レジュームフラグをTrueに設定し、途中経過を保存して終了する
                resume_flag = True
                continue
        # レジュームフラグがTrueであればスキップ
        else:
            resume_flag = False
            print(f"{url} をスキップします。")

        # 進捗状況を更新
        pbar.update(1)

    # tqdmをクローズ
    pbar.close()

    # 途中経過が保存されている場合は残りの処理をスキップ
    if not resume_flag:
        df = pd.DataFrame(products, columns=['商品名', '販売価格', 'レアリティ', '商品コード', 'シリーズ', 'カード種類', 'レギュレーション'])
        df.to_csv('products.csv', index=False, encoding='utf-8-sig')

except Exception as e:
    traceback.print_exc()
    print(f"エラーが発生しました: {e}")
    print("途中経過を保存して終了します。")
    # レジュームフラグをTrueに設定し、途中経過を保存して終了する
    resume_flag = True

# WebDriverを終了する
driver.quit()
