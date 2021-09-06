# from enlighten_inference import EnlightenOnnxModel
import os
import shutil
import ssl
from collections import OrderedDict

import torch


def bypass_ssl_verify():
    if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
        ssl._create_default_https_context = ssl._create_unverified_context

def save_img(filepath, img):
    import cv2
    # cv2.imwrite(filepath,cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
    cv2.imwrite(filepath, img)


def clear_folder(folder_name):
    a = os.listdir(folder_name)
    for file_ in a:
        os.remove(os.path.join(folder_name, file_))
    print(str(len(a)) + " files in '" + folder_name + "' folder deleted")


def empty_dir(dir_path: str):
    for filename in os.listdir(dir_path):
        file_path = os.path.join(dir_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def load_checkpoint(model, weights: str, use_cpu: bool = True):
    checkpoint = torch.load(weights, map_location='cpu') if use_cpu else torch.load(weights)
    try:
        model.load_state_dict(checkpoint["state_dict"])
    except:
        state_dict = checkpoint["state_dict"]
        new_state_dict = OrderedDict()
        for k, v in state_dict.items():
            name = k[7:]  # remove `module.`
            new_state_dict[name] = v
        model.load_state_dict(new_state_dict)
