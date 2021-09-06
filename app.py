import time

from flask import Flask, request
from flask_cors import CORS
from py_profiler.profiler_controller import profiler_blueprint

from enhance_service import *

app = Flask(__name__)
app.register_blueprint(profiler_blueprint)
CORS(app)

folder_out = "static/output/"
os.makedirs(folder_out, exist_ok=True)

enhance_service = EnhanceService(
    'Deblurring/pretrained_models/model_deblurring.pth',
    use_cpu=True
)


@app.route('/')
def index():
    return "hello"


@app.route('/enhance', methods=['POST'])
def enhance():
    urls = dict(request.get_json())['urls']
    #
    begin = time.time()
    output_result = enhance_service.process(urls, folder_out)
    print(f'Output: {output_result}')
    return {
        'time': time.time() - begin,
        'result': output_result
    }


if __name__ == '__main__':
    app.run()
