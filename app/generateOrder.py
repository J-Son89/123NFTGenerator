from app.generateImages import startGenerateImages
from app.generateMetadata import startGenerateMetadata
from app.downloadImages import getImagesFolder, getOutputImagesFolder, getOutputMetadataFolder,getOrderFolder
from app.s3 import upload_with_default_configuration
import os 
import shutil
from zipfile import ZipFile

bucket = '123nft'

def getPathForS3(orderId, fileName):
    return orderId + "/order/" + fileName

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

def cleanUp(orderId):
    remove(orderId)
        
def zipFiles(orderId,collectionName):
    # specifying the zip file name
    fileName = getOrderFolder(orderId) + os.sep + collectionName + ".zip"
    filePaths = getAllFilePaths(getOrderFolder(orderId))

    with ZipFile(fileName,'w') as zip:
       # writing each file one by one
           for file in filePaths:
               zip.write(file)
 
    return fileName
        
def zipFilesAndUpload(orderId, collectionName):
    fileName = zipFiles(orderId,collectionName)
    upload_with_default_configuration(fileName,bucket,  getPathForS3(orderId, collectionName + ".zip"),os.path.getsize(fileName) )
    
def startGenerateOrder(request, startIndex,endIndex):
    metadata = request['data']['orderData']['metadata']
    imageUrlsMap = request['data']['orderData']['imageUrlsMap']
    projectLayersDepth = request['data']['orderData']['projectLayersDepth']
    collectionName = request['data']['orderData']['collectionDetails']['collectionName']
    orderId = request['data']['_id']
    
    metadataFormat = request['data']['orderData']['orderDetails']['metadata']['value']
    
    startGenerateImages(metadata[startIndex:endIndex], imageUrlsMap, projectLayersDepth, orderId)
    
    startGenerateMetadata(metadata[startIndex:endIndex], metadataFormat, orderId)
    
    zipFilesAndUpload(orderId, collectionName)
    
    
    cleanUp(orderId)
    return {'id':orderId}
    
    
    

