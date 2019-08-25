from io import StringIO
import json
from os import environ

import boto3
from datetime import datetime as dt
import pandas as pd
import requests


def hello(event, context):
    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event
    }
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return responses


def fetch(event, context):
    symbols = ["SPY", "TLT", "QQQ", "EEM", "USO"]
    symbol_files = []

    for symbol in symbols:
        interval = "1min"

        params = {
            "symbol": symbol,
            "apikey": environ['ALPHAADVANTAGE'],
            "function": "TIME_SERIES_INTRADAY",
            "interval": interval,
            "outputsize": "full"
        }

        url = "https://www.alphavantage.co/query"
        res = requests.get(url, params=params)

        key = f"Time Series ({interval})"
        ts = res.json()[key]

        result = []

        for time_str, data in ts.items():
            dp = {"timestamp": time_str, "symbol": symbol}
            for k,v in data.items():
                field = k.split(" ")[1]
                dp[field] = v
            result.append(dp)

        df = pd.DataFrame(result)

        fn = f"{symbol}_{interval}.json"
        dt_str = dt.today().strftime('%Y-%m-%d')

        write_to_s3 = (environ['WRITE_TO_S3'] == 'true')

        if write_to_s3:
            file_url = f"s3://{environ['BUCKETNAME']}/{dt_str}/{fn}"
        else:
            from os import makedirs, path
            file_url = f'local_data/{dt_str}/{fn}'
            makedirs(path.dirname(file_url), exist_ok=True)

        df.to_json(file_url)
        symbol_files.append(file_url)


    body = {
        "message": f"Successfully saved {symbols} data",
        "symbol_files": symbol_files
    }
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response
