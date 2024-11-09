import requests
import platform
import os
import json
import zipfile
from datetime import datetime


def get_url(version: str) -> bool | dict:
    # Checando o Chromedriver
    response: requests.Response = requests.get(
        'https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json'
    )

    if response.status_code != 200:
        print(f'Falha na requisição. Status code: {response.status_code}')
        return False

    # Obter o JSON da resposta
    json_data: dict = response.json()

    # Obter a versão do Chrome
    new_version: str = json_data['channels']['Stable']['version']
    if version == new_version:
        print(f'Chromedriver está na versão atual: {version}')
        return False

    # Obter a sistema operacional
    pc_info: dict = platform.uname()

    # Ajustar a nomenclatura do sistema operacional com a plataforma do chromedriver
    match pc_info.system[:3].lower():
        case 'win':
            platform_info: str = 'win' + pc_info.machine[-2:]
        case 'mac':
            raise ('Necessita configuração para sistemas mac')
        case 'lin':
            raise ('Necessita configuração para sistemas Linux')
        case _:
            raise (f'Necessita configuração para sistemas {pc_info.system}')

    # Obter a url
    data: list[dict] = json_data['channels']['Stable']['downloads']['chromedriver']
    for item in data:
        if item['platform'] == platform_info:
            return {'version': new_version, 'url': item['url']}

    # Caso a plataforma não seja encontrada
    raise (f'Não foi encontrada a plataforma {platform_info}.')


def update() -> None:
    json_file_name: str = 'chromedriver-version.json'
    if not os.path.exists(json_file_name):
        with open(json_file_name, 'w') as file:
            json.dump({'version': ''}, file, indent=4)

    with open(json_file_name, 'r') as file:
        version: str = json.load(file)['version']

    url: str | bool = get_url(version)
    if not url:
        return

    with requests.get(url['url'], stream=True) as response:
        if response.status_code != 200:
            raise (f'Falha na requisição. Status code: {response.status_code}')

        zip_file_name: str = 'chromedriver.zip'
        with open(zip_file_name, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        with zipfile.ZipFile(zip_file_name, 'r') as file:
            file.extractall()

        os.remove(zip_file_name)

    with open(json_file_name, 'w') as file:
        json.dump(
            {'version': url['version'], 'date_of_download': datetime.now().strftime("%d/%m/%Y %H:%M:%S")},
            file,
            indent=4,
        )

    print('Chromedriver baixado com sucesso!')
