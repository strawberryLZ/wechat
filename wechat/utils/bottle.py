import sys
import logging

from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client

def bottleSEND(file):
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    secret_id = 'AKIDmU1RccS3UltpZ88knfMtETYUEmDSgoAL'  # 替换为用户的 secretId
    secret_key = 'OghXUIzVp0zmOpcGleT2QceZKtHWZS9J'  # 替换为用户的 secretKey
    region = 'ap-chengdu'  # 替换为用户的 Region
    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
    # 2. 获取客户端对象
    client = CosS3Client(config)
    # 3.创建桶子
    '''
     response = client.create_bucket(
     sBucket='examplebucket-1250000000'
    '''
    with open(file, 'rb') as fp:
        response = client.put_object(
            Bucket='lzw-1301082773',
            Body=fp,
            Key=file,
            StorageClass='STANDARD',
            EnableMD5=False
        )
    print(response['ETag'])