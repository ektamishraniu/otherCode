winpty ssh.exe -i sand-box-ac-keypair.pem ec2-user@18.217.177.107

mkdir -p python
python3.7 -m venv pg8000scramp
cd pg8000scramp
source bin/activate
pip install pg8000
pip install scramp
cp -r /home/ec2-user/pg8000scramp/lib/python3.7/site-packages/* /home/ec2-user/python/
deactivate
cd
zip -r pg8000scramp.zip python


import json
import boto3
import os
import glob
import shutil

s3c = boto3.client('s3')
s3r = boto3.resource('s3')

#sourceBucket   = "medpro-conversion-input"
#fileName       = "s1p/plainCsvFile.csv"
#anaFileName:  plainCsvFile-analysis.txt   targetFile:  s1p/plainCsvFile-analysis.txt    srcFileName:  plainCsvFile.csv
def cleanTmp(fileName):
    srcFileName = os.path.basename(fileName)
    tmpfiles = glob.glob(os.path.join('/tmp/*'))
    print("Following Files In Tmp will be attempt to delete: ", tmpfiles)
    for root, dirs, files in os.walk('/tmp', topdown=False):
        for name in files:
            if srcFileName in name:
                print("removing file:  ",name)
                os.remove(os.path.join(root, name))
        for name in dirs:
            if srcFileName in name:
                print("removing file in dir:  ",name)
                shutil.rmtree(os.path.join(root, name), ignore_errors=True)
                #os.rmdir(os.path.join(root, name))
    tmpfiles = glob.glob(os.path.join('/tmp/*'))
    print("After Removal, files left in tmp   : ", tmpfiles) 
    '''
    for file in tmpfiles:
        try:
            os.remove(file)  
        except:
            print("Error while deleting file/folder: ", file)
    '''

def getFilesNamePath(sourceBucket, fileName):
    srcFileName = os.path.basename(fileName)
    srcFileFrac = os.path.splitext(fileName)[0].rsplit('/')
    srcFilePath = ""
    if len(srcFileFrac)>1:
        srcFilePath = os.path.splitext(fileName)[0].rsplit('/', 1)[0] + "/"   
    anaFileName = srcFileName + "-analysis.txt"
    targetFile = os.path.join(srcFilePath + anaFileName)
    return (srcFileName, anaFileName, targetFile)

def cpToTmpFolder(sourceBucket, fileName, anaFileName=""):#Copy File to Tmp Folder
    print("copying: ", sourceBucket,"/",fileName,"   to /tmp/",anaFileName)
    #cleanTmp(fileName)
    if anaFileName is "":
        anaFileName = fileName
    s3c.download_file(sourceBucket, fileName, '/tmp/' + anaFileName)
    return

def cpFrmTmpToS3(sourceBucket, targetFile, anaFileName):#Copy from Tmp To S3
    tmpfiles = glob.glob(os.path.join('/tmp/*'))
    print("all files in tmp: ", tmpfiles)
    print("copying file: ",anaFileName, "    to S3: ",sourceBucket,"/",targetFile)
    s3r.Object(sourceBucket, targetFile).put(Body=open('/tmp/' + anaFileName, 'rb'))
    return
