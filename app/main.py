from flask import Flask, request
from app.generateOrder import startGenerateOrder
from flask_cors import CORS
from threading import Thread


app = Flask(__name__)
CORS(app, resources={
     r"/generateOrder/*": {"origins": "https://backend123nft.herokuapp.com"}})

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


# check header for auth
@app.route('/generateOrder', methods=['GET', 'POST'])
def fulfillOrder():
    if request.content_type != 'application/json':

        print('Invalid content-type. Must be application/json.')
        return
    if request.method == 'POST':
        data = request.json
        metadata = data['data']['orderData']['metadata']

        startIndex = 0
        endIndex = len(metadata)
        thread = Thread(target=startGenerateOrder,
                        args=(data, startIndex, endIndex))
        thread.start()
        orderId = data['data']['_id']

        return {'id': orderId}
