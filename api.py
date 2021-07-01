from dotenv import load_dotenv
load_dotenv()
from flask import Flask, jsonify
import pickle, sys, os, redis, atexit, requests
import pandas as pd
import numpy as np

import googleapiclient.discovery
import logging
from extensions import cache
from predict import predict
from flask_cors import CORS


logging.getLogger('googleapicliet.discovery_cache').setLevel(logging.ERROR)

#TODO: Implement route cacheing
#TODO: Check what is consuming time.
#processs 


app = Flask(__name__)
cache.init_app(app)
CORS(app)
redis_client = redis.Redis(host="localhost", port=6379)

cache_dict = {}

@atexit.register
def clear_redis_db():
    redis_client.flushdb()
    print("Redis cache cleaned!")


def simple_cache(max_cache_size=1000000):
    def simple_cache_decorator(func):
        def wrapper(id, data, thumbnail):
            print(cache_dict)
            cache_value = cache_dict.get(id, None) # get cache data if not then None
            if cache_value: # if cache the increase the count of the value and return the cached value
                redis_client.incr(id)
                return cache_value
            cache_count = redis_client.incr("CACHE_COUNT")
            if cache_count > max_cache_size: #if cache length is more than the specified length remove the least used cache
                min_value = float("inf")
                min_key = None
                for key in cache_dict:
                    key_count = int(redis_client.get(key))
                    if key_count < min_value:
                        min_value = key_count
                        min_key = key
                if min_key: # delete cache with minnimum call count
                    redis_client.delete(key)
                    del cache_dict[key]
                redis_client.decr("CACHE_COUNT")
            # create a cache with the value of the returned function return the result to.
            res = func(id, data, thumbnail)
            cache_dict[id] = res
            redis_client.incr(id)
            return res
        return  wrapper
    return simple_cache_decorator


@cache.memoize(50)
def get_data(id):
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = os.environ["CLEAN_TUBE_KEY"]

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = DEVELOPER_KEY)

    request = youtube.videos().list(id=id, part="statistics, snippet")
    response = request.execute()
    thumbnail = response["items"][0]["snippet"]["thumbnails"]['high']
    if not response["items"]:
        return jsonify(status="error", message="Invalid Video ID"), 400
    statistics = response['items'][0]["statistics"]
    # features = ["video_title", "video_views","video_likes", "video_dislikes", "video_comments"]
    data = {}
    data["video_title"] =  response['items'][0]["snippet"]["title"]
    data["video_views"] = float(statistics['viewCount'])
    data["video_likes"] = float(statistics["likeCount"])
    data["video_dislikes"] = float(statistics["dislikeCount"])
    data["video_comments"] = float(statistics["commentCount"])
    data["thumbnail"] = thumbnail["url"]

    return data


@simple_cache(3)
def predict_metadata(id, data, thumbnail):
    if not data : return None
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    # print(thumbnail)
    req = requests.get(f"https://us-central1-daring-feat-282021.cloudfunctions.net/predict_image?vid={thumbnail}")
    if req.status_code == 200:
        image_score = req.json()["result"]
    else:
        raise ValueError(req.json()["message"])

    return image_score

@app.route("/")
def home():
    return jsonify(result="Hello World!")


@app.route("/predict-clickbait/<id>")
def predict_video(id):
    try:
        data = get_data(id)
        metadata_score = predict_metadata(id, data, data["thumbnail"])
        return jsonify(score=metadata_score, name=data["video_title"], _id=id), 200
    except Exception as e:
        return jsonify(status="error", message="Sorry an Unknown error occured!", response=str(e)), 400

if __name__ == "__main__":
    app.run(debug=True, port=5001)