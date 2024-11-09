import requests
from bs4 import BeautifulSoup
import os
import json
import urllib
from plyer import notification
import webbrowser


def main() -> None:
    response: requests.Response = requests.get('https://www.consulpam.com.br/index.php?menu=concursos&acao=ver&id=511')

    if response.status_code != 200:
        print(f'Falha na requisição. Status code: {response.status_code}')
        return

    # # print('Tipo de conteúdo:', response.headers.get('Content-Type'))
    # with open('result.html', 'w', encoding='utf-8') as file:
    #     file.write(response.text)
    #     # print(response.text)

    soup: BeautifulSoup = BeautifulSoup(response.text, 'lxml')
    links: list[str] = [link['href'] for link in soup.find_all('a', href=True) if link['href'][:9] == 'arquivos/']

    json_file_name: str = 'links-found.json'
    if not os.path.exists(json_file_name):
        with open(json_file_name, 'w') as file:
            json.dump({'links': []}, file, indent=4)

    with open(json_file_name, 'r') as file:
        old_links: list[str] = json.load(file)['links']

    for link in links:
        if link not in old_links:
            url: str = urllib.parse.quote(f'https://www.consulpam.com.br/{link}', safe=":/?&=")
            notification.notify(title='Concurso Russas', message='Novo arquivo encontrado', timeout=20)
            webbrowser.open(url)
            old_links.append(link)

    with open(json_file_name, 'w') as file:
        json.dump({'links': old_links}, file, indent=4)


if __name__ == '__main__':
    main()
