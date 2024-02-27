from colorama  import Fore
import capsolver

from utils.utils import print_colored

def capsolver_solver(api_key:str, 
                     websitePublicKey:str="2CB16598-CB82-4CF7-B332-5990DB66F3AB", 
                     websiteURL:str="https://twitter.com/i/flow/signup"
                     ) -> str:
    capsolver.api_key = api_key
    print_colored(text="SOLVING CAPTCHA...", color=Fore.LIGHTBLUE_EX)
    return capsolver.solve({
        "type": "FunCaptchaTaskProxyLess",
        "websitePublicKey": websitePublicKey,
        "websiteURL": websiteURL,
    })["token"]