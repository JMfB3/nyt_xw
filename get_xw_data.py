
import os
import json
import requests
from bs4 import BeautifulSoup as bs
import datetime
import boto3


start_date = datetime.date(1970, 1, 1)
end_date = datetime.date(1979, 12, 31)
start_str = start_date.strftime("%Y_%m_%d")
end_str = end_date.strftime("%Y_%m_%d")

aws_access_key = os.environ.get("AWS_ACCESS_KEY")
aws_access_secret = os.environ.get("AWS_ACCESS_SECRET")

def build_dates():
    """
    Build a list of dates for which we want to get all crossword entries
    """
  
    now = datetime.datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    print("start", current_time)

    dates = []
    curr_date = start_date
    while curr_date <= end_date:
        dates.append(curr_date.strftime("%m/%d/%Y"))
        curr_date += datetime.timedelta(days=1)

    get_html(dates)

    now = datetime.datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    print("end", current_time)

    return None


def get_html(dates):
    """
    For each date, get html from the url and use soup to get all entries for that date
    """

    for xw_date in dates:
        print(xw_date)
        url = f"https://www.xwordinfo.com/PS?date={xw_date}"
        response = requests.get(url)
        s = str(response.content, "utf-8")
        soup = bs(s, "html.parser")
        l = soup.find_all("a", href=True, class_=None)
        ll = [{xw_date: i.contents[0]} for i in l if "Finder" in i.get("href")]

        upload_to_s3(ll, xw_date)

    return None


def upload_to_s3(all_words, dt):
    """
    Save data in s3
    """

    ds = dt.replace("/", "_")

    filepath = f"~/all_xw_words_{ds}.json"
    wf = json.dumps(all_words)
    with open(filepath, "x") as f:
        f.write(wf)

    session = boto3.Session(aws_access_key_id=aws_access_key, aws_secret_access_key=aws_access_secret)
    s3 = session.resource('s3')
    s3.meta.client.upload_file(
        Filename=filepath,
        Bucket="bucket",
        Key=f"key/all_words_{ds}.json"
    )

    os.remove(filepath)


if __name__ == "__main__":
    dates = build_dates()
