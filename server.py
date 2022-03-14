from flask import Flask, request
from generateOrder import startGenerateOrder
app = Flask(__name__)




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
        startGenerateOrder(data, startIndex, endIndex)
        

if __name__ == '__main__':
    app.run(host="localhost", port=8000, debug=True)
