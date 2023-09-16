import requests 
def collect_data():
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        # 'Cookie': '_kmid=3614cb7370f0a72edcdebc5f28d47c71; _kmfvt=1691752467; site_version=desktop; _gcl_au=1.1.607725920.1691752474; _ym_uid=1691752475415895915; _ym_d=1691752475; uad=1281658864d6182d8276a566497485; userId=12816588; _kmwl=1; list_type_sdisplay=table; _ga_RFREXLZKKJ=GS1.2.1692453352.5.1.1692453805.60.0.0; RORSSQIHEK=55a54a90d827d9b8e80ea46b25f50338; slrememberme=12816588_%242y%2410%24W.Gza6CeC3WnC2eK2YUrveBzmTGu2LSQtjZWcc5aIo0HWbQGxA6r6; _ga_5PPLL9HRHT=GS1.1.1693389670.5.0.1693389670.60.0.0; _ga=GA1.2.1503615656.1691752474; _gid=GA1.2.822398492.1693389671; yandex_client_id=1691752475415895915; google_client_id=1503615656.1691752474; _ym_isad=1; _ubtcuid=cllxkhnrn00002vf1551k0fzb; _sp_ses.b695=*; _sp_id.b695=a3d0aaa5-6b90-48a4-9714-090444f41871.1691752475.10.1693389776.1692455274.2db039b3-85ed-4e09-b354-834449207507',
        'DNT': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
    }

    r = requests.get(url="https://kwork.ru/projects?c=all", headers=headers)
    if r.status_code == 200:
        pass 
    else:
        print("Kwork parser failed")

def main():
    collect_data()

if __name__ == '__main__':
     main()