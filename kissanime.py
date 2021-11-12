#!/usr/bin/python
import logging
import argparse
import re
import requests
from bs4 import BeautifulSoup as bs
from tqdm import tqdm

headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0"}
download_pat = re.compile("download\W*\(\d+p\W*mp4\)", re.IGNORECASE)
quality_pat = re.compile("\d+p", re.IGNORECASE)


def get_gogo(vid_link):

    stream = requests.get(vid_link, headers=headers)
    stream_sp = bs(stream.text, features="lxml")
    try:
        gog_lnk=stream_sp.iframe.get("src").replace("streaming.php", "download")
    except AttributeError:
        return None
    gog = requests.get(gog_lnk, headers=headers)
    referer=gog.url
    gog_sp = bs(gog.text, features="lxml")
    links = gog_sp.find_all("a")
    # valid download links
    q_links = [lnk for lnk in links if download_pat.fullmatch(lnk.text)]
    try:
        lnk_dct = {quality_pat.search(lnk.text).group():lnk.get("href") for lnk in q_links}
    except AttributeError:
        return None
    return (referer, lnk_dct)

def download_gogo(link, referer=None):
    # this redirects to another which should not be followed but to go to location lnk manually
    r_resp = requests.get(link, allow_redirects=False, headers=headers)
    headers["referer"] = "https://gogoplay1.com/"
    r_lnk = r_resp.headers.get("Location")
    flname = r_lnk.split("?")[0].split("/")[-1]
    with requests.get(r_lnk, headers=headers, stream=True) as r:
         r.raise_for_status()
         file_size = int(r.headers.get('Content-Length', 0))
         bar = tqdm(total=file_size, unit='iB', unit_scale=True)
         with open(flname, "wb") as f:
             for chunk in r.iter_content(chunk_size=8192):
                 bar.update(len(chunk))
                 f.write(chunk)
         bar.close
    headers.pop("referer")


if __name__ == "__main__":
    referer,gogo_lnk = get_gogo("https://ww2.kissanimes.tv/watch/pokemon-2019-dub-episode-60")
    download_gogo( gogo_lnk.get("360P"), referer=referer)
