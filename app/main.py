import requests
from flask import Flask, request
from generateOrder import startGenerateOrder
app = Flask(__name__)


app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


# check header for auth
@app.route('/generateOrder', methods=['GET', 'POST'])
def fulfillOrder():
    if request.content_type != 'application/json':

        print('Invalid content-type. Must be application/json.')
        return
    if request.method == 'POST':
        data = request.json
        startIndex = 0
        endIndex = 8
        result = startGenerateOrder(data, startIndex, endIndex)
        return result


if __name__ == '__main__':
    app.run(host="https://generator-123nft.herokuapp.com/", port=8000, )
