from flask import Flask, request
from app.generateOrder import startGenerateOrder
from flask_cors import CORS
from threading import Thread
import shutil
from zipfile import ZipFile
import requests
from app.downloadImages import getImagesFolder, getOutputImagesFolder, getOutputMetadataFolder, getOrderFolder
from app.s3 import upload_with_default_configuration
import os

bucket = '123nft'

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

        totalImages = len(metadata)

        thread = Thread(target=batchJobs,
                        args=(data, totalImages))
        thread.start()
        orderId = data['data']['_id']

        return {'id': orderId}


def getAllFilePaths(directory):

    # initializing empty file paths list
    file_paths = []

    # crawling through directory and subdirectories
    for root, directories, files in os.walk(directory):
        for filename in files:
            # join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)

    # returning all file paths
    return file_paths


def remove(path):
    """ param <path> could either be relative or absolute. """
    if os.path.isfile(path) or os.path.islink(path):
        os.remove(path)  # remove the file
    elif os.path.isdir(path):
        shutil.rmtree(path)  # remove dir and all contains
    else:
        raise ValueError("file {} is not a file or dir.".format(path))


def getPathForS3(orderId, fileName):
    return orderId + "/order/" + fileName


def cleanUp(orderId):
    remove(orderId)


def zipFiles(orderId, collectionName):
    # specifying the zip file name
    fileName = getOrderFolder(orderId) + os.sep + collectionName + ".zip"
    filePaths = getAllFilePaths(getOrderFolder(orderId))

    with ZipFile(fileName, 'w') as zip:
       # writing each file one by one
        for file in filePaths:
            zip.write(file)

    return fileName


def zipFilesAndUpload(orderId, collectionName):
    fileName = zipFiles(orderId, collectionName)
    upload_with_default_configuration(fileName, bucket,  getPathForS3(
        orderId, collectionName + ".zip"), os.path.getsize(fileName))


def batchJobs(data, totalImages):
    threads = []
    """
    for i in range(4):
        startIndex = int(i * (totalImages/4))
        endIndex = int(startIndex + (totalImages/4))
        # We start one thread per url present.
        process = Thread(target=startGenerateOrder,
                         args=(data, startIndex, endIndex))

        process.start()
        threads.append(process)
    # We now pause execution on the main thread by 'joining' all of our started threads.
    # This ensures that each has finished processing the urls.
    for process in threads:
        process.join()

    collectionName = data['data']['orderData']['collectionDetails']['collectionName']

    zipFilesAndUpload(orderId, collectionName)

    cleanUp(orderId)
    """
    orderId = data['data']['_id']

    requests.post('https://backend123nft.herokuapp.com/orderComplete',
                  data={'orderID': orderId})
