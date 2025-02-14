import sys
import os
import hashlib
import hmac
import base64
import requests
import time
import json
import datetime

def commonFunc(lst):

    pList=lst

    timestamp = int(time.time() * 1000)
    timestamp = str(timestamp)
        
    access_key = "D6826154BFF47DE9775D"
    secret_key = "50BDD4517D5E8A72A7CDEAF48E01CE5AF1A3B793"
    secret_key = bytes(secret_key, 'UTF-8')
        
    api_server = "https://ncloud.apigw.ntruss.com"
    api_url = "/vserver/v2/" + pList[0]
    api_url = api_url + "?responseFormatType=json&regionCode=KR"
    #print(api_url)
    if len(pList) > 1:
        api_url = api_url + pList[1]

    method = "GET"

    message = method + " " + api_url + "\n" + timestamp + "\n" + access_key
    message = bytes(message, 'UTF-8')
        
    signingKey = base64.b64encode(hmac.new(secret_key, message, digestmod=hashlib.sha256).digest())
        
    http_header = {
        "x-ncp-apigw-signature-v2" : signingKey,
        "x-ncp-apigw-timestamp" : str(timestamp),
        "x-ncp-iam-access-key" : access_key,
    }

    return api_server+api_url, http_header

 # 1. 서버 목록 조회
def getServerInstanceList():
    pList=['getServerInstanceList']
    url, http_header=commonFunc(pList)

    server_response = requests.get(url, headers=http_header)
    data = json.loads(server_response.text)

    serverCnt = data['getServerInstanceListResponse']['totalRows']
    serverList = data['getServerInstanceListResponse']['serverInstanceList']
    # kvm, xen, etc 로 서버 하이퍼바이저 구분
    kvmServerList=[]
    xenServerList=[]
    etcServerList=[]

    for i in range(serverCnt):
        serverDict = {}
        serverDict['serverInstanceNo'] = serverList[i]['serverInstanceNo']
        serverDict['serverName'] = serverList[i]['serverName']
        serverDict['hypervisorType'] = serverList[i]['hypervisorType']['codeName']
        serverDict['serverInstanceStatus'] = serverList[i]['serverInstanceStatus']['code']

        # hypervisorType 구분 저장 (KVM/XEN/ETC)
        if serverDict['hypervisorType'] == "KVM":
            kvmServerList.append(serverDict)
        elif serverDict['hypervisorType'] == "XEN":
            xenServerList.append(serverDict)
        else:
            etcServerList.append(serverDict)

    print("kvmServerList: ",kvmServerList)
    print("xenServerList: ",xenServerList)
    print("etcServerList: ",etcServerList)

    return kvmServerList, xenServerList, etcServerList

if __name__ == '__main__':
    getServerInstanceList()