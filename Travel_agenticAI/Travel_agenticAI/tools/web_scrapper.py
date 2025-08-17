# api calling not working for visa requirements and safety ratings, I can use web scraping for that
from fileinput import filename
import requests
from bs4 import BeautifulSoup
import os
import json
import time
from typing import Dict, Any
from models.llm_generator import build_llm
from data.visa_data_class import ExtractedVisaInfo
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from geopy.geocoders import Nominatim

class LLMWebScrapper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
        }

        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.llm = build_llm()
        self.structured_visa_llm = self.llm.with_structured_output(ExtractedVisaInfo)

        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--disable-extensions')
        self.chrome_options.add_argument('--disable-logging')
        # self.chrome_options.add_argument('--start-maximized')
        self.chrome_options.add_argument('--disable-web-security')
        self.chrome_options.add_argument('--allow-running-insecure-content')
        self.chrome_options.add_argument(f"user-agent={self.headers['User-Agent']}")
        self.chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Main callable function that inturn calls the other 2 functions
    def scrape_visa_requirements(self, destination_country: str, passport_country: str = "India") -> Dict[str, Any]:
        
        source_data = []

        visa_index_data = self.scrape_visa_index(destination_country, passport_country)
        if visa_index_data and 'error' not in visa_index_data:
            source_data.append({
                'source': 'visa_index_static',
                'data': visa_index_data
            })
        interactive_visa_data = self.check_visa_requirements(destination_country, passport_country)        
        if interactive_visa_data and 'error' not in interactive_visa_data:
            source_data.append({
                'source': 'visa_index_interactive',
                'data': interactive_visa_data
            })

        return {
            'destination_country': destination_country,
            'passport_country': passport_country,
            'sources': source_data,
            'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_sources': len(source_data)
        }

    def scrape_visa_index (self, destination_country: str, passport_country: str) -> Dict[str, Any]:
        
        output_dir = "scraped_data"
        os.makedirs(output_dir, exist_ok=True)
        filename = f"{output_dir}/visa_requirements.json"
        
        try:
            dest_input = destination_country.strip()
            dest_country = self.city_to_country(dest_input)
            
            country_slug = None
            if dest_country.lower() in ["united kingdom", "uk", "britain"]:
                country_slug = "uk"
            elif dest_country.lower() in ["united states", "united states of america", "usa", "us"]:
                country_slug = "us"
            elif dest_country.lower() in ["united arab emirates", "uae"]:
                country_slug = "uae"
            else:
                country_slug = dest_country.lower().replace(" ", "-")

            url = f"https://visaindex.com/visa/{country_slug}-visa/"
            response = self.session.get(url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            for element in soup(['script', 'style', 'nav', 'footer']):
                element.decompose()
            
            page_content = soup.get_text(separator='\n', strip=True)

            print("Processing content with LLM...")
            visa_info = self.structured_visa_llm.invoke(f"""
            Extract visa requirement information for {passport_country} citizens traveling to {destination_country} from this webpage content:
            
            {page_content}
            
            Focus on:
            - Visa requirement type (visa free, visa on arrival, e-visa, visa required)
            - Maximum stay duration
            - Processing time and requirements
            - Any special conditions or restrictions
            """)

            visa_info_dict = visa_info.dict() if hasattr(visa_info, 'dict') else dict(visa_info)
            
            country_key = dest_country
            self.save_visa_info(filename, country_key, visa_info_dict)

            return visa_info_dict
        
        except Exception as e:
            print(f"ERROR in scrape_visa_index: {e}")
            return {'error': f'VisaIndex scraping failed {str(e)}'}
    
    def check_visa_requirements(self, destination_country: str, passport_country: str) -> Dict[str, Any]:

        driver = webdriver.Chrome(options=self.chrome_options)
        
        try:
            url = f"https://visaindex.com/"
            driver.get(url)
            wait = WebDriverWait(driver, 10)
            try: 
                initial_button = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div/div[2]/button")))
                initial_button.click()
            except Exception as e:
                print(f"ERROR in check_visa_requirements: {e}")
                print("Initial pop-up button not found or not needed.")

            passport_dropdown = wait.until(EC.element_to_be_clickable((By.ID, "passport_to")))
            select_passport = Select(passport_dropdown)
            select_passport.select_by_visible_text(passport_country)

            destination_dropdown = wait.until(EC.element_to_be_clickable((By.ID, "passport_from")))
            select_destination = Select(destination_dropdown)
            select_destination.select_by_visible_text(destination_country)

            submit_button = driver.find_element(By.XPATH, "/html/body/div[4]/div/div[2]/div[3]/button")
            submit_button.click()

            time.sleep(8)

            visa_page_source = driver.page_source
            soup = BeautifulSoup(visa_page_source, 'html.parser')

            for element in soup(['script', 'style', 'nav', 'footer', 'header']):
                element.decompose()
        
            content_text = soup.get_text(separator='\n', strip=True)

            visa_info = self.structured_visa_llm.invoke(f"""
            Extract visa requirement information for {passport_country} citizens traveling to {destination_country} from this webpage:
            {content_text}
            """)
            
            return visa_info.dict()
        except Exception as e:
            print(f"ERROR in check_visa_requirements: {e}")
            return {'error': f'VisaIndex (interactive) scraping failed: {str(e)}'}
        finally:
            driver.quit()

    def save_visa_info(self, filename, country_key, visa_info_dict):

        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                try:
                    data_cache = json.load(f)
                except Exception:
                    data_cache = {}
        else:
            data_cache = {}

        country_key_lc = country_key.strip().lower()
        if country_key_lc not in data_cache:
            data_cache[country_key_lc] = visa_info_dict

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data_cache, f, ensure_ascii=False, indent=4)
        else:
            print(f"Data for {country_key_lc} already present—no write needed.")

    def city_to_country(self, city: str) -> str:
        geolocator = Nominatim(user_agent="my_travel_agent")
        location = geolocator.geocode(city, addressdetails=True, language='en')
        if location and 'country' in location.raw['address']:
            return location.raw['address']['country']
        return city