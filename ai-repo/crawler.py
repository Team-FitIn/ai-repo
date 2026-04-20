import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# 1. 연결 설정
options = Options()
options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def crawl_final_refined():
    print(f"✅ 연결 확인: {driver.title}")
    
    # 현재 페이지에서 모든 상품 링크 수집
    all_links = []
    # 무신사 상품 상세 주소 패턴 추출
    elements = driver.find_elements(By.TAG_NAME, "a")
    for el in elements:
        href = el.get_attribute("href")
        if href and ("/products/" in href or "/app/goods/" in href):
            if href not in all_links:
                all_links.append(href)
        if len(all_links) >= 30: break

    print(f"🔗 수집 대상: {len(all_links)}개 상품")

    product_data = []
    for idx, link in enumerate(all_links):
        try:
            driver.get(link)
            time.sleep(random.uniform(3, 5)) 

            # [수정된 핵심 로직] 알려주신 태그 정보 반영
            # 1. 상품명 추출 (span 태그 및 MDS 데이터 속성 활용)
            name = "상품명 찾기 실패"
            name_elements = driver.find_elements(By.CSS_SELECTOR, "span[data-mds='Typography']")
            for ne in name_elements:
                # 클래스명에 GoodsName이 들어간 span을 찾습니다.
                if "GoodsName" in ne.get_attribute("class"):
                    name = ne.text
                    break

            # 2. 이미지 URL 추출 (Swiper 클래스 활용)
            img_url = ""
            img_elements = driver.find_elements(By.CSS_SELECTOR, "img.Swiper__Img-sc-j9bha0-8, img[class*='Swiper__Img']")
            if img_elements:
                img_url = img_elements[0].get_attribute("src")
            else:
                # 예비용: 아까 확인한 큰 이미지 ID
                img_url = driver.find_element(By.ID, "detail_bigimg").get_attribute("src") if driver.find_elements(By.ID, "detail_bigimg") else ""

            product_data.append({
                "id": idx + 1,
                "name": name,
                "img_url": img_url,
                "link": link
            })
            print(f"[{idx+1}/{len(all_links)}] ✅ {name} 수집 성공")
            
        except Exception as e:
            print(f"[{idx+1}] 실패")
            continue
            
    return product_data

# 실행 및 저장
try:
    data = crawl_final_refined()
    if data:
        df = pd.DataFrame(data)
        df.to_json("musinsa_tops.json", orient="records", force_ascii=False, indent=4)
        print(f"\n✨ {len(data)}개 데이터 저장 완료! 이제 JSON을 열어보세요.")
except Exception as e:
    print(f"오류: {e}")