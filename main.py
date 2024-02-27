import configparser
from colorama import Fore
from httpx import Client
import re

from utils.captcha import capsolver_solver
from utils.utils import print_colored



config = configparser.ConfigParser()
config.read('config.ini')

CAPSOLVER = config.get('API', 'CAPSOLVER_API')

class Account:

    def __init__(self, cookies:dict, proxy:str) -> None:
        self.cookies = cookies
        self.url = "https://twitter.com/account/access"
        self.client = Client(timeout=30, follow_redirects=True, proxies=proxy)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
            "Accept": "*/*",
            "Accept-Language": "en-GB,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Sec-GPC": "1",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "script",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Site": "same-origin",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "TE": "trailers"
        }

        self._tokens = {}


    
    def __extract_tokens_from_access_html_page(self, html:str):
        pattern = re.compile(r'name="authenticity_token" value="([^"]+)"|name="assignment_token" value="([^"]+)"')
        
        if matches := pattern.findall(html):
            authenticity_token = matches[0][0] if matches[0][0] else matches[0][1]
            assignment_token = matches[1][0] if matches[1][0] else matches[1][1]
            self._tokens = {"authenticity_token": authenticity_token,
                    "assignment_token": assignment_token}
            
    
    def __js_inst(self):
        js_script = self.client.get(
            url="https://twitter.com/i/js_inst?c_name=ui_metrics"
            ).text
        pattern = re.compile(r'return\s*({.*?});', re.DOTALL)
        js_instr = pattern.search(js_script)

        return js_instr.group(1)
    
    def __get_access_page(self):
        res = self.client.get(self.url, headers=self.headers, cookies=self.cookies)
        self.cookies.update(dict(res.cookies))
        self.__extract_tokens_from_access_html_page(html=res.text)

    
    def __post_to_accces_page(self, data:dict):
        headers = self.headers
        headers["Host"] = "twitter.com"
        headers["Origin"] = "https://twitter.com"
        headers["Referer"] = "https://twitter.com/account/access"

        res = self.client.post(f"{self.url}?lang=en", data=data, headers=headers, cookies=self.cookies)
        self.cookies.update(dict(res.cookies))
        self.__extract_tokens_from_access_html_page(html=res.text)
    
    
    def __data_with_js_inst(self, tokens:dict) -> dict:
        return {
            "authenticity_token": tokens["authenticity_token"],
            "assignment_token": tokens["assignment_token"],
            "lang": "en",
            "flow": "",
            "ui_metrics": self.__js_inst()
        }
    
    def __data_with_funcaptcha(self, tokens:dict, fun_captcha_token:str) -> dict:
        return {
                "authenticity_token": tokens["authenticity_token"],
                "assignment_token": tokens["assignment_token"],
                'lang': 'en',
                'flow': '',
                'verification_string': fun_captcha_token, 
                'language_code': 'en'
            }
    
    def __post_data_with_token(self, fun_captcha_token:str):
        data = self.__data_with_funcaptcha(tokens=self._tokens, fun_captcha_token=fun_captcha_token)
        self.__post_to_accces_page(data=data)
    
    def __post_data_with_js_inst(self):
        data = self.__data_with_js_inst(tokens=self._tokens)
        self.__post_to_accces_page(data=data)

    
    def unlock(self):
        print_colored(text="UNLOCKING ACCOUNT...", color=Fore.GREEN)
        self.__get_access_page()

        self.__post_data_with_js_inst()

        fun_captcha_token = capsolver_solver(api_key=CAPSOLVER,
                        websitePublicKey="0152B4EB-D2DC-460A-89A1-629838B529C9",
                        websiteURL="https://twitter.com")
            
        self.__post_data_with_token(fun_captcha_token=fun_captcha_token)


        fun_captcha_token = capsolver_solver(api_key=CAPSOLVER,
                         websitePublicKey="0152B4EB-D2DC-460A-89A1-629838B529C9",
                         websiteURL="https://twitter.com")
        
        self.__post_data_with_token(fun_captcha_token=fun_captcha_token)

        self.__post_data_with_js_inst()
        print_colored(text="ACCOUNT UNLOCKED...", color=Fore.GREEN)

"""
Example usage
"""

client = Account(
    # Fill in the auth token and ct0 cookies of the account you wanna unlock
    cookies={
    "auth_token": "",
    "ct0": ""
},
    # the proxy is a must it shout be in "http://ip:port" or "http://username:password@ip:port"
    # Get the best proxy from the best provider => https://iproyal.com/?r=SeasonedCode
    proxy=""
)
client.unlock()
