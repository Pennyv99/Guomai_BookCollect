from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import pyodbc


def add_to_database(tags):
    # 连接 SQL Server
    server = '172.16.10.75'
    database = 'Booooks'
    account = 'sa'
    password = 'gm123456'

    # 创建连接字符串
    conn_str = f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={server};DATABASE={database};UID={account};PWD={password};TrustServerCertificate=yes;"

    try:
        # 连接数据库
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        # 删除重复的行（确保表名一致）
        for tag in tags:
            cursor.execute('''
            DELETE FROM Lookup
            WHERE LookupKey = ?
            ''', (tag,))

        # 插入数据
        for tag in tags:
            cursor.execute('''
            INSERT INTO Lookup (LookupName, LookupKey, LookupValue)
            VALUES (?, ?, ?)
            ''', ('DoubanTag', tag, tag))

        # 提交事务
        conn.commit()
        print("数据已成功插入到数据库。")

    except Exception as e:
        print("数据库操作时发生错误:", e)
    finally:
        # 确保关闭数据库连接
        cursor.close()
        conn.close()


# 启动 ChromeDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# 访问目标 URL
url = 'https://book.douban.com/tag/?view=type&icn=index-sorttags-all'
driver.get(url)

# 等待页面加载
time.sleep(3)

# 抓取所有符合条件的 <a> 元素
try:
    # 查找 class 为 tagCol 的 table 下所有的 <a> 标签
    elements = driver.find_elements(By.XPATH, '//*[@class="tagCol"]//a')
    tags = [element.text for element in elements]

    # 打印所有找到的 <a> 标签的文本内容
    for i, tag in enumerate(tags):
        print(f"标签 {i + 1}: {tag}")

    # 将标签插入数据库
    add_to_database(tags)

except Exception as e:
    print("未找到指定的元素或发生错误:", e)

# 关闭浏览器
driver.quit()
