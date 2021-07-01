import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import tensorflow as tf
import tensorflow_hub as hub
from google.cloud import storage
from PIL import Image
from urllib.error import URLError

import re
import numpy as np
import urllib
import warnings
# warnings.filterwarnings("ignore")

IMAGE_RES = 224


#A2Gh4PBt9k4
def predict_image(request):
    """ 
    Predicts if a given image is clickbait or not given its url.

    @param img_url : str
        url of image to predict.
    @return :
        A scalar value represeting the probability of the image being clickbait.
    """
    img_url = request.args.get("vid")
    thumbnail_party = re.compile(r"(https|http)://(i.ytimg.com|img.youtube.com)/vi/[a-zA-Z0-9_-]{11}/hqdefault.jpg")
    print("LOG:", img_url, type(img_url))
    if img_url is None:
        return {"message":"invalid video id"}, 400

    if thumbnail_party.match(img_url) is None:
        return {"message":"Invalid thubnail link"}, 400

    model_path = "/tmp/models/"
    client = storage.Client()
    bucket = client.get_bucket("cleantube_model")
    saved_model = bucket.blob("1609964765/saved_model.pb")
    var1 = bucket.blob("1609964765/variables/variables.data-00000-of-00001")
    var2 = bucket.blob("1609964765/variables/variables.index")
    if not os.path.exists(model_path):
        os.mkdir(model_path)
        os.mkdir(os.path.join(model_path, "variables"))
    saved_model.download_to_filename(os.path.join(model_path,"saved_model.pb"))
    var1.download_to_filename(os.path.join(model_path, "variables","variables.data-00000-of-00001"))
    var2.download_to_filename(os.path.join(model_path, "variables","variables.index"))

    print("Downloaded models")
    try:
        model = tf.keras.models.load_model(model_path, custom_objects={"KerasLayer": hub.KerasLayer})
        im = Image.open(urllib.request.urlopen(img_url))

        im_vec = np.array(im.resize((IMAGE_RES, IMAGE_RES)), dtype=np.float32)
        im_vec /= 255.0
        predict = model.predict(im_vec[np.newaxis, ...])
        res = float(predict[0][1])
        return {"result": res}, 200
    except URLError as e:
        return {"status": "error", "message":"bad url address", "response": str(e)}, 400
    except Exception as e:
        return {"status": "error", "message": str(e)}, 400