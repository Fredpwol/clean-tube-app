import requests
import threading, time

video_ids = ["Y_ZZv--OI0s","6e_e4r57sq8","UkTEsbk1XH0","XUbAHtYz_Fg","038wccyPIno","PQ8YCjJ7cpA","giaHYo4YZ8E","84AkUJ75GsM","W8TcZchxJtI"]

def get_score(v_id):
    print("Called get score with video id "+ v_id)
    response = requests.get(f"http://localhost:5001/predict-clickbait/{v_id}")
    print("got response of "+ v_id,response.json())

start = time.time()
threads = []
for v_id in video_ids:
    t = threading.Thread(target=get_score, args=(v_id,))
    t.start()
    threads.append(t)

for t in threads:
    t.join()

print("Finished all test time Elaspsed ", time.time() - start)	

