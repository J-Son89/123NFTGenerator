import requests
from flask import Flask, request
from generateOrder import startGenerateOrder
app = Flask(__name__)


app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


# check header for auth
@app.route('/generateOrder', methods=['GET','POST'])
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
        # return  {'id':'3412d30c1947d76171d99236c1b778be'}
        # requests.post("http://localhost:5000/orderFulfilled", {'id':'3412d30c1947d76171d99236c1b778be'})
        
if __name__ == '__main__':
    app.run(host="localhost", port=8000, )

