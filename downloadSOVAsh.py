"""Downloads SOVA comics using last number already downloded files."""

import os
from os.path import join
import threading
import subprocess
import bs4
import requests
import logging
import pretty_errors

def downloadSOVAsh(startComic, endComic):
    """Загуржает комиксы в указанном диапазаоне

    :param startComic: с какого
    :param endComic: по какой включительно
    """
    local = threading.local()
    logging.info(f"Start {startComic}, End {endComic}")
    for urlNumber in range(startComic, endComic + 1):
        # Download the page.
        with lock:
            print('Downloading page https://acomics.ru/~sovaeffective/{}...'.format(urlNumber))
            logging.info(f"{urlNumber} Downloading page https://acomics.ru/~sovaeffective/{urlNumber}")
        local.res = requests.get('https://acomics.ru/~sovaeffective/{}'.format(urlNumber))
        try:
            local.res.raise_for_status()
        except requests.exceptions.HTTPError as ex:
            with lock:
                print('Not found: {}\n{}'.format(local.res.url, ex))
                logging.info(f'{urlNumber} Not found: {local.res.url}')
                logging.error(ex)
            continue

        local.soup = bs4.BeautifulSoup(local.res.text, 'html.parser')

        # Find the URL of the comic image.
        local.comicElem = local.soup.select('#mainImage')
        if not local.comicElem:
            with lock:
                print('Could not find comic image.')
                logging.info(f'{urlNumber} Could not find comic image.')
        else:
            local.comicUrl = "https://acomics.ru" + local.comicElem[0].get('src')
            local.savePath = os.path.join(resDir, os.path.basename(local.comicUrl))
            if not os.path.exists(local.savePath):
                # Download the image.
                with lock:
                    print('Downloading image {}...'.format(local.comicUrl))
                    logging.info(f'{urlNumber} Downloading image {local.comicUrl}')
                local.res = requests.get(local.comicUrl)
                local.res.raise_for_status()

                # Save the image
                local.imageFile = open(local.savePath, 'wb')
                for chunk in local.res.iter_content(100000):
                    local.imageFile.write(chunk)
                local.imageFile.close()
                downloadedFiles.append(local.savePath)
                with lock:
                    logging.info(f'{urlNumber} Image saved {local.savePath}')
            else:
                logging.info(f'{urlNumber} Image exist {local.savePath}')


if __name__ == '__main__':
    resDir = r'O:\Мои документы\Мои рисунки\SOVA'
    os.makedirs(resDir, exist_ok=True)
    downloadedFiles = []

    logging.basicConfig(level=logging.INFO, format=' %(asctime)s - %(levelname)s - %(message)s',
                        filename=join(resDir, 'logs.log'))

    maxI = max([int(f.split("-")[0]) for f in os.listdir(resDir) if f.endswith('.jpg')]) + 1
    print("maxI: {}".format(maxI))
    logging.info(f"maxI: {maxI}")

    # Create and start the Thread objects.
    downloadThreads = []
    lock = threading.Lock()
    for i in range(maxI, maxI + 20, 4):
        downloadThread = threading.Thread(target=downloadSOVAsh, args=(i, i + 3))
        downloadThreads.append(downloadThread)
        downloadThread.start()

    # Wait for all threads to end.
    for downloadThread in downloadThreads:
        downloadThread.join()
    print('Done.')
    logging.info(f"Done.")

    if downloadedFiles:
        res = "\n".join(downloadedFiles)
    else:
        res = "No new comics!"

    with open(os.path.join(resDir, 'result.txt'), 'w') as f:
        f.write(resDir + "\n")
        f.write(res)

    subprocess.Popen([r"C:\WINDOWS\system32\notepad.exe", os.path.join(resDir, 'result.txt')], shell=True)
