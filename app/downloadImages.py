import requests # to get image from the web
import shutil # to save it locally
import os


def addFolder(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

## Set up the image URL and filename

def download(imageUrl,filename, orderId):
    
    # Open the url image, set stream to True, this will return the stream content.
    r = requests.get(imageUrl, stream = True)

# Check if the image was retrieved successfully
    if r.status_code == 200:
    # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
        r.raw.decode_content = True
    
    # Open a local file with wb ( write binary ) permission.
    with open( getImagesPath(filename,orderId),'wb') as f:
        shutil.copyfileobj(r.raw, f)
        
    return

def downloadAll(imageUrlsMap, rootName, layerNames, orderId):
    addFolder(getImagesFolder(orderId))
    for layer in layerNames:
        for imageName in imageUrlsMap[rootName][layer]:
            download(imageUrlsMap[rootName][layer][imageName], imageName, orderId)

def getImagesFolder(orderId):
    return  orderId + os.sep + "local" 

def getImagesPath(filename,orderId):
    return getImagesFolder(orderId) +os.sep+ filename

def getOrderFolder(orderId):
    return  orderId + os.sep + "order"
    
def getOutputImagesFolder(orderId):
    return getOrderFolder(orderId) + os.sep + "images"

def getOutputImagesPath(filename,orderId):
    return getOutputImagesFolder(orderId) +os.sep+ filename

def getOutputMetadataFolder(orderId):
    return getOrderFolder(orderId) + os.sep + "metadata"

def getOutputMetadataPath(filename,orderId):
    return getOutputMetadataFolder(orderId) +os.sep+ filename


# base combinations folder
def getBaseCombinationsOutputImagesFolder(orderId):
    return  orderId + os.sep + "baseCombinations"
    