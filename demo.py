import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms.functional as TF
from PIL import Image
import os
from runpy import run_path
from skimage import img_as_ubyte
from collections import OrderedDict
from natsort import natsorted
from glob import glob
import cv2
import argparse
#from enlighten_inference import EnlightenOnnxModel
import time
import numpy as np
import os
from IAGCWD import White_Balancer
from CEIQ import CEIQ

# from MEON_demo import MEON_eval
# torch.cuda.set_per_process_memory_fraction(0.8, device=None)
# torch.cuda.empty_cache()
# os.environ["CUDA_VISIBLE_DEVICES"]=""



def save_img(filepath, img):
    # cv2.imwrite(filepath,cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
    cv2.imwrite(filepath, img)

def load_checkpoint(model, weights):
    checkpoint = torch.load(weights)
    # checkpoint = torch.load(weights, map_location='cpu')
    try:
        model.load_state_dict(checkpoint["state_dict"])
    except:
        state_dict = checkpoint["state_dict"]
        new_state_dict = OrderedDict()
        for k, v in state_dict.items():
            name = k[7:] # remove `module.`
            new_state_dict[name] = v
        model.load_state_dict(new_state_dict)

task    = 'Deblurring'

#os.makedirs(out_dir, exist_ok=True)

# Remove all files in these two folder
import os, shutil
def empty_dir(dir):
    for filename in os.listdir(dir):
        file_path = os.path.join(dir, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
#empty_dir(out_dir)
print("Flushing successfully")
def process(inp_dir, enhanced_out_dir):
    files = natsorted(glob(os.path.join(inp_dir, '*.jpg'))
                    + glob(os.path.join(inp_dir, '*.JPG'))
                    + glob(os.path.join(inp_dir, '*.jpeg'))
                    + glob(os.path.join(inp_dir, '*.JPEG'))
                    + glob(os.path.join(inp_dir, '*.png'))
                    + glob(os.path.join(inp_dir, '*.PNG')))

    if len(files) == 0:
        raise Exception(f"No files found at {inp_dir}")

    # Load corresponding model architecture and weights
    load_file = run_path(os.path.join(task, "MPRNet.py"))
    model = load_file['MPRNet']()
    model.cuda()

    weights = os.path.join(task, "pretrained_models", "model_"+task.lower()+".pth")
    load_checkpoint(model, weights)
    model.eval()

    img_multiple_of = 8
    #enlighten_model = EnlightenOnnxModel()

    start_time = time.monotonic()
    print('Number of files: ', len(files))
    # print(files)

    white_balancer = White_Balancer()
    # Load CEIQ model
    CEIQ_model = CEIQ()

    for file_ in files:
        img = Image.open(file_).convert('RGB')
        input_ = TF.to_tensor(img).unsqueeze(0).cuda()
        # input_ = TF.to_tensor(img).unsqueeze(0)


        # Pad the input if not_multiple_of 8
        h,w = input_.shape[2], input_.shape[3]
        H,W = ((h+img_multiple_of)//img_multiple_of)*img_multiple_of, ((w+img_multiple_of)//img_multiple_of)*img_multiple_of
        padh = H-h if h%img_multiple_of!=0 else 0
        padw = W-w if w%img_multiple_of!=0 else 0
        input_ = F.pad(input_, (0,padw,0,padh), 'reflect')

        with torch.no_grad():
            restored = model(input_)
        restored = restored[0]
        restored = torch.clamp(restored, 0, 1)

        # Unpad the output
        restored = restored[:,:,:h,:w]
        restored = restored.permute(0, 2, 3, 1).cpu().detach().numpy()

        restored = img_as_ubyte(restored[0])
        # processed = enlighten_model.predict(cv2.cvtColor(restored, cv2.COLOR_RGB2BGR))
        # processed = img_as_ubyte(processed)

        ### White balancing ###
        # Extract intensity component of the image
        deblurred_img = cv2.cvtColor(restored, cv2.COLOR_RGB2BGR)
        YCrCb = cv2.cvtColor(deblurred_img, cv2.COLOR_BGR2YCrCb)
        Y = YCrCb[:,:,0]
        # Determine whether image is bright or dimmed
        threshold = 0.3
        exp_in = 112 # Expected global average intensity 
        M,N = deblurred_img.shape[:2]
        mean_in = np.sum(Y/(M*N)) 
        t = (mean_in - exp_in)/ exp_in

        # Process image for gamma correction
        img_output = None
        if t < -threshold: # Dimmed Image
            print (file_ + ": Dimmed")
            result = white_balancer.process_dimmed(Y)
            YCrCb[:,:,0] = result
            img_output = cv2.cvtColor(YCrCb,cv2.COLOR_YCrCb2BGR)
        elif t > threshold:
            print (file_ + ": Bright Image") # Bright Image
            result = white_balancer.process_bright(Y)
            YCrCb[:,:,0] = result
            img_output = cv2.cvtColor(YCrCb,cv2.COLOR_YCrCb2BGR)
        else:
            img_output = deblurred_img

        restored = cv2.cvtColor(restored, cv2.COLOR_RGB2BGR)
        
        # Compute CEIQ score and decide whether the image was significantly enhanced or not
        # org_score = CEIQ_model.predict(np.expand_dims(restored, axis=0), 1)[0]
        # imp_score = CEIQ_model.predict(np.expand_dims(img_output, axis=0), 1)[0]
        scores = CEIQ_model.predict([restored, img_output], 1)
        # if file_.split('/')[-1] == '20210420050550-de27_wm.jpg':
        #     save_img(os.path.join('tmp_folder', f+'[restored].png'), restored)
        #     save_img(os.path.join('tmp_folder', f+'[img_output].png'), img_output)
        #     print(f"Scoreeeee: {(scores[0], scores[1])}")
        if scores[0] > scores[1]:
            img_output = restored
        
        f = os.path.splitext(os.path.split(file_)[-1])[0]
        #save_img(os.path.join(out_dir, f+'.png'), restored)
        save_img(os.path.join(enhanced_out_dir, f+'.png'), img_output)
        # cv2.imwrite(os.path.join(enhanced_out_dir, f+'.png'), img_output)

    print(f"Processing Time: {time.monotonic() - start_time}")
    print(f"Enhanced images saved at {enhanced_out_dir}")
