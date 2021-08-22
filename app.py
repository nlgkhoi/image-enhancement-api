from flask import Flask, render_template, request, jsonify, send_from_directory, abort,send_file
from flask_cors import CORS
import time

from demo import *
from preprocessing_img import *

app = Flask(__name__)
CORS(app)
client_count=0 #to seperate 

@app.route('/')
def index():
  return "hello"

@app.route('/enhance',methods=['POST', 'GET'])
def enhance0():
  if request.method == 'POST':
    global client_count
    urls=dict(request.get_json())['urls']
    #
    folder_in="static/clients/input/"+format(client_count,'04d')+"/"
    folder_out="static/clients/output/"+format(client_count,'04d')+"/"
    #
    try:
      os.makedirs(folder_in)
    except:
      pass
    try:
      os.makedirs(folder_out)
    except:
      pass
    clear_folder(folder_in)
    clear_folder(folder_out)
    begin=time.time()
    im_pre=Im_preprocess()
    im_pre.close()
    im_pre.from_urls_to_array(urls)
    im_pre.write_img(folder_in)

    process(folder_in,folder_out)

    img_files=os.listdir(folder_out)
    img_files.sort()

    return_list=[]
    for i in im_pre.correct_idx:
      return_list.append({
          'before':urls[im_pre.correct_idx[i]],
          'after':'/get_image/'+format(client_count,'04d')+'/'+img_files[i]
      })
    client_count+=1
    if client_count%499==0:
      client_count=0
    return {
        'time':time.time()-begin,
        'result':return_list
    }
  return {'message':'You need to use POST metod'}


@app.route('/get_image/<int:client_count>/<img_name>')
def get_image(client_count,img_name):
    print('./static/clients/output'+format(client_count,'04d')+"/"+img_name)
    return send_file('./static/clients/output/'+format(client_count,'04d')+"/"+img_name,attachment_filename=img_name,as_attachment=False)

if __name__ == '__main__':
    app.run()