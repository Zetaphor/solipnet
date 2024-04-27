import os
import json
import requests
import random
import re
from flask import url_for
from openai import OpenAI
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from json_repair import repair_json

load_dotenv()
class SolinetEngine:
    def __init__(self):
        self.client = OpenAI(base_url=os.getenv("BASE_URL"), api_key=os.getenv("API_KEY"))
        self.internet_db = dict()

        self.max_tokens = int(os.getenv("LLM_MAX_TOKENS"))

        self.enable_images = bool(os.getenv("ENABLE_IMAGES"))

        self.prompts = dict()
        self.load_prompts()

    def load_prompts(self, filename="prompts.json"):
        try:
            with open(filename, 'r') as file:
                data = json.load(file)
                self.prompts = data

                if self.enable_images:
                    self.prompts['system_prompt'] = data['system_prompt_with_images']
                else:
                    self.prompts['system_prompt'] = data['system_prompt_without_images']
        except FileNotFoundError:
            print(f"Error: The file {filename} does not exist.")
        except json.JSONDecodeError:
            print("Error: The prompts file is not a valid JSON.")
        except Exception as e:
            print(f"An error occurred loading the prompts: {e}")

    def image_search(self, keyword):
        url = os.getenv("SEARXNG_URL")

        params = {
            'q': keyword,
            'format': 'json',
            'categories': 'images'
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if data['results']:
                return data['results'][0]['img_src']  # Return the source URL of the first image
            else:
                return None

        except requests.RequestException as e:
            print(f"Error fetching image: {e}")
            return "https://via.placeholder.com/100"

    def _format_page(self, dirty_html):
        soup = BeautifulSoup(dirty_html, "html.parser")

        # Remove any TailwindCSS links, we want to use our local copy
        tailwind_css = soup.find('link', rel='stylesheet', href=True)
        if tailwind_css:
            tailwind_css.decompose()

        head_tag = soup.find('head')
        if head_tag:
            tailwind_css_link = soup.new_tag('link', rel='stylesheet', type='text/css', href=url_for('static', filename='css/tailwind.min.css'))
            head_tag.append(tailwind_css_link)

        # Replace any https references to keep the link database consistent
        for a in soup.find_all("a"):
            href = a.get("href", "")
            if "mailto:" in href:
                continue
            clean_href = href.replace("http://", "").replace("https://", "")
            a["href"] = "/" + clean_href

        # Update and adjust image tags
        for img in soup.find_all("img"):
            if "width" not in img.attrs:
                # Assign a random width between 100 and 300px if width is not present
                img["width"] = str(random.randint(100, 300))
            else:
                # Use regular expression to find digits in the width value
                width = re.findall(r'\d+', img["width"])[0]
                max_width = re.findall(r'\d+', os.getenv("MAX_IMAGE_WIDTH"))[0]

                if int(width) > int(max_width):
                    img["width"] = max_width

            alt_text = img.get("alt", "")
            new_src = self.image_search(alt_text)
            img["src"] = new_src

        return str(soup)

    def get_page(self, url, path, search_query=None):
        # Return already generated page if already generated page
        try: return self.internet_db[url][path]
        except: pass

        prompt = self.prompts['page_prompt'].replace("{url}", url).replace("{path}", path)

        # Add other pages to the prompt if they exist
        if url in self.internet_db and len(self.internet_db[url]) > 1:
            pass

        generated_page_completion = self.client.chat.completions.create(messages=[
            {
                "role": "system",
                "content": self.prompts['system_prompt']
            },
            {
                "role": "user",
                "content": prompt
            }],
            model="llama3",
            temperature=self.prompts['page_prompt_temperature'],
            max_tokens=self.max_tokens
        )

        generated_page = generated_page_completion.choices[0].message.content
        open("tmp/curpage.html", "w+").write(generated_page)
        generated_page = self._format_page(generated_page)

        if not url in self.internet_db:
            self.internet_db[url] = dict()
        self.internet_db[url][path] = generated_page

        return generated_page

    def fix_malformed_json(self, malformed_json):
        malformed_json = malformed_json.replace('\n', '')

        with open("tmp/search_results.json", "w") as file:
            file.write(malformed_json)

        fixed_json = repair_json(malformed_json)

        with open("tmp/fixed_search_results.json", "w") as file:
            file.write(fixed_json)

        try:
            valid_json = json.loads(fixed_json)
            return valid_json
        except json.JSONDecodeError as e:
            print(f"Error fixing JSON: {e}")
            return None

    def parse_search_results(self, results_string):
        results = self.fix_malformed_json(results_string)

        if results_string is not None:
            if isinstance(results, dict):
                if "results" in results:
                    results = results["results"]
            elif isinstance(results, list):
                if "results" in results[0]:
                    # The results key is returned in an array
                    results = results[0]["results"]
                else:
                    # The results key is missing and it's just a list of results
                    return results

            return results
        else:
            print("Error parsing search results")
            return {}


    def get_search(self, query):
        query_prompt = self.prompts['search_prompt'].replace("{query}", query)
        search_results_completion = self.client.chat.completions.create(messages=[
            {
                "role": "system",
                "content": self.prompts['search_system_prompt']
            },
            {
                "role": "user",
                "content": query_prompt
            }],
            model="llama3",
            temperature=self.prompts['search_prompt_temperature'],
            max_tokens=self.max_tokens
        )

        search_results = self.parse_search_results(search_results_completion.choices[0].message.content)

        return search_results

    def export_internet(self, filename="internet.json"):
        json.dump(self.internet_db, open(filename, "w+"))
