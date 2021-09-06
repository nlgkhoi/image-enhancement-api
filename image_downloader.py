import io
from concurrent import futures
from concurrent.futures import ThreadPoolExecutor
from typing import Dict
from urllib.request import Request, urlopen

from PIL import Image
from py_profiler import profiler


class ImageDownloader:

    def __init__(self, num_threads: int = 8):
        self.num_threads = num_threads
        self.executor = ThreadPoolExecutor(max_workers=num_threads)

    def bulk_download_as_image(self, image_urls: list) -> dict:

        r: Dict[str, bytearray] = self.bulk_download(image_urls)

        result_dict = {}
        for k, v in r.items():
            result_dict[k] = Image.open(io.BytesIO(v))

        return result_dict

    @profiler(f'{__qualname__}.bulk_download')
    def bulk_download(self, image_urls: list) -> Dict[str, bytearray]:
        future_to_checks = {
            self.executor.submit(self.download_url, url): url
            for url in image_urls
        }

        result_dict = {}
        # Now it comes to the result of each check
        # The try-except-else clause is omitted here
        for future in futures.as_completed(future_to_checks):
            url = future_to_checks[future]
            image_bytearray = future.result()

            result_dict[url] = image_bytearray

        return result_dict

    def download_url(self, path: str) -> bytearray:
        pass


class HybirdImageDownloader(ImageDownloader):

    @profiler("download_url")
    def download_url(self, path: str) -> bytearray:
        if path.startswith('http:') or path.startswith('https:'):
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
            }
            import ssl
            gcontext = ssl.SSLContext()
            req = Request(path, headers=headers)
            res = urlopen(req, context=gcontext)
            raw = bytearray(res.read())
        else:
            with open(path, 'rb') as reader:
                raw = bytearray(reader.read())
        return raw
