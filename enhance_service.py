import logging
import os
# from enlighten_inference import EnlightenOnnxModel
import uuid
from concurrent import futures
from concurrent.futures import ThreadPoolExecutor
from typing import List

import cv2
import numpy as np
import torch
import torch.nn.functional as F
import torchvision.transforms.functional as TF
from py_profiler import profiler
from skimage import img_as_ubyte

from CEIQ import CEIQ
from Deblurring.MPRNet import MPRNet
# from MEON_demo import MEON_eval
# torch.cuda.set_per_process_memory_fraction(0.8, device=None)
# torch.cuda.empty_cache()
# os.environ["CUDA_VISIBLE_DEVICES"]=""
from image_downloader import HybirdImageDownloader
from utils.model_utils import load_checkpoint, save_img
from white_balancer import WhiteBalancer


class EnhanceService:

    def __init__(self,
                 deblur_model_path,
                 use_cpu: bool = True,
                 use_deblur_model: bool = False,
                 enhanced_output_only: bool = False,
                 ):
        self.use_cpu = use_cpu
        self.use_deblur_model = use_deblur_model
        self.enhanced_output_only = enhanced_output_only
        # Executor to run enhance process concurrently
        self.executor = ThreadPoolExecutor(max_workers=8)
        # A downloader to download image using a thread pool with 16 threads
        self.image_downloader = HybirdImageDownloader(16)

        # task = 'Deblurring'
        # load_file = run_path(os.path.join(task, "MPRNet.py"))
        # model = load_file['MPRNet']()  # Type: MPRNet
        self.deblur_model = MPRNet()
        if self.use_cpu is not True:
            self.deblur_model.cuda()

        load_checkpoint(self.deblur_model, deblur_model_path, use_cpu=use_cpu)
        self.deblur_model.eval()

        self.white_balancer = WhiteBalancer()
        self.ceiq_scoring_model = CEIQ()

        logging.info(f'white_balancer: {type(self.white_balancer)}')
        logging.info(f'CEIQ_model: {type(self.ceiq_scoring_model)}')
        logging.info(f'Model: {type(self.deblur_model)}')
        logging.info("Init successfully")

    @profiler()
    def process(self, image_urls: List[str], enhanced_out_dir):
        image_dict = self.image_downloader.bulk_download_as_image(image_urls)
        if len(image_urls) == 0:
            raise Exception(f"No image urls found at {image_urls}")
        logging.info('Number of files: %d', len(image_dict))

        future_to_checks = {
            self.executor.submit(self._enhance_image, image, 8, enhanced_out_dir): url
            for url, image in image_dict.items()
        }

        result_dict = {}
        # Now it comes to the result of each check
        # The try-except-else clause is omitted here
        for future in futures.as_completed(future_to_checks):
            url = future_to_checks[future]
            output_path, enhanced_score = future.result()
            result_dict[url] = {
                'enhanced_url': output_path,
                'enhanced_score': enhanced_score
            }
        return result_dict

    @profiler()
    def _enhance_image(self, image, factor, out_dir) -> [str, float]:
        restored = self._deblur_image(image, factor) if self.use_deblur_model else np.asarray(image)
        # processed = enlighten_model.predict(cv2.cvtColor(restored, cv2.COLOR_RGB2BGR))
        # processed = img_as_ubyte(processed)
        img_output = self._process_white_balancing(restored)

        restored = cv2.cvtColor(restored, cv2.COLOR_RGB2BGR)
        origin_score, improved_score = self._calc_score([restored, img_output])
        if origin_score > improved_score and self.enhanced_output_only:
            img_output = restored

        output_path = os.path.join(out_dir, f'{uuid.uuid1()}.jpg')
        save_img(output_path, img_output)

        return [output_path, ((improved_score - origin_score) / origin_score)]

    @profiler()
    def _deblur_image(self, img, factor: int = 8):
        img = img.convert('RGB')
        input_image_as_tensor = TF.to_tensor(img).unsqueeze(0) if self.use_cpu else TF.to_tensor(img).unsqueeze(
            0).cuda()

        # Pad the input if not_multiple_of 8
        h, w = input_image_as_tensor.shape[2], input_image_as_tensor.shape[3]
        H, W = ((h + factor) // factor) * factor, (
                (w + factor) // factor) * factor
        padh = H - h if h % factor != 0 else 0
        padw = W - w if w % factor != 0 else 0
        input_image_as_tensor = F.pad(input_image_as_tensor, (0, padw, 0, padh), 'reflect')

        with torch.no_grad():
            restored = self.deblur_model(input_image_as_tensor)
        restored = restored[0]
        restored = torch.clamp(restored, 0, 1)

        # Unpad the output
        restored = restored[:, :, :h, :w]
        restored = restored.permute(0, 2, 3, 1).cpu().detach().numpy()
        restored = img_as_ubyte(restored[0])

        return restored

    @profiler()
    def _process_white_balancing(self, input_image, threshold: float = 0.3):
        ### White balancing ###
        # Extract intensity component of the image
        deblurred_img = cv2.cvtColor(input_image, cv2.COLOR_RGB2BGR)
        YCrCb = cv2.cvtColor(deblurred_img, cv2.COLOR_BGR2YCrCb)
        Y = YCrCb[:, :, 0]
        # Determine whether image is bright or dimmed

        exp_in = 112  # Expected global average intensity
        M, N = deblurred_img.shape[:2]
        mean_in = np.sum(Y / (M * N))
        t = (mean_in - exp_in) / exp_in

        # Process image for gamma correction
        output_image = None
        if t < -threshold:  # Dimmed Image
            logging.info('Dimmed')
            result = self.white_balancer.process_dimmed(Y)
            YCrCb[:, :, 0] = result
            output_image = cv2.cvtColor(YCrCb, cv2.COLOR_YCrCb2BGR)
        elif t > threshold:
            logging.info('Bright Image')  # Bright Image
            result = self.white_balancer.process_bright(Y)
            YCrCb[:, :, 0] = result
            output_image = cv2.cvtColor(YCrCb, cv2.COLOR_YCrCb2BGR)
        else:
            output_image = deblurred_img

        return output_image

    @profiler()
    def _calc_score(self, images):
        # Compute CEIQ score and decide whether the image was significantly enhanced or not
        # org_score = CEIQ_model.predict(np.expand_dims(restored, axis=0), 1)[0]
        # imp_score = CEIQ_model.predict(np.expand_dims(img_output, axis=0), 1)[0]
        scores = self.ceiq_scoring_model.predict(images, option=1)
        logging.info(f"Scores: {scores[0]} -> {scores[1]}: Improved: {((scores[1] - scores[0]) * 100 / scores[0])} %")
        return scores
