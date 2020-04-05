def upload(file_obj, key, bucket="lzw-1301082773"):
    # file_obj = request.FILES.get('file')
    # print(file_obj.name)
    # key = file_obj.name.rsplit(".")[-1]
    # print(key)
    from qcloud_cos import CosConfig
    from qcloud_cos import CosS3Client

    secret_id = 'AKIDmU1RccS3UltpZ88knfMtETYUEmDSgoAL'  # 替换为用户的 secretId
    secret_key = 'OghXUIzVp0zmOpcGleT2QceZKtHWZS9J'  # 替换为用户的 secretKey
    region = 'ap-chengdu'  # 替换为用户的 Region
    token = None  # 使用临时密钥需要传入 Token，默认为空，可不填
    scheme = 'https'  # 指定使用 http/https 协议来访问 COS，默认为 https，可不填
    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)
    # 2. 获取客户端对象
    client = CosS3Client(config)
    response = client.upload_file_from_buffer(
        Bucket='lzw-1301082773',
        Body=file_obj,
        Key=key
    )
    print('111', response)
    return "https://{0}.cos.{1}.myqcloud.com/{2}".format(bucket, region, key)
