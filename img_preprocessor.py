import threading

from skimage import io

from utils.model_utils import bypass_ssl_verify

bypass_ssl_verify()
mutex = threading.Lock()


class ImgPreprocessor:
    correct_idx = []  # index in urls that have been downloaded normally
    img_list = []

    def from_urls_to_array(self, urls):
        threads = []
        for i, url in enumerate(urls):
            t = threading.Thread(target=self.load_one_image, args=[url, i])
            t.start()
            threads.append(t)

        for thread in threads:
            thread.join()

    def load_one_image(self, url, i):
        try:
            print(f'Load image: {url}')
            img = io.imread(url)  # load concurrently

            mutex.acquire()  # mutex lock
            self.img_list.append(img)
            self.correct_idx.append(i)
            mutex.release()  # mutex release
        except Exception as err:
            print(err)
            pass

    def write_img(self, path):
        for idx, img in enumerate(self.img_list):
            print(f'Save image: {idx}: {len(img)}')
            io.imsave(path + format(idx, '04d') + ".png", img)

    def close(self):
        self.correct_idx = []
        self.img_list = []
