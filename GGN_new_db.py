import requests
import uuid
import re

import requests
from datetime import datetime
import time

from operator import itemgetter
import country


def check_ggn_new(producerId):
    producerId = str(producerId)
    BASE = "https://prod.osapiens.cloud"
    PAGE = (
        f"{BASE}/portal/webbundle/foodplus/field-service-os/"
        "supply-chain-portal?app-route-hash=%252Fcertificates"
    )

    session = requests.Session()

    common_headers = {
        "accept": "*/*",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "user-agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/145.0.0.0 Safari/537.36"
        ),
    }

    # 1) bootstrap a fresh anonymous session
    page_resp = session.get(PAGE, headers=common_headers, timeout=30)

    # print("PAGE STATUS:", page_resp.status_code)
    # print("COOKIES AFTER PAGE LOAD:")
    cookie = ""
    for c in session.cookies:
        cookie = c.value

    # 2) fetch xsrf token using the new session
    xsrf_resp = session.get(
        f"{BASE}/portal/xsrf",
        headers={
            **common_headers,
            "content-type": "text/plain; charset=utf-8",
            "referer": PAGE,
        },
        timeout=30,
    )

    # print("XSRF STATUS:", xsrf_resp.status_code)
    # print("XSRF BODY:", xsrf_resp.text)

    csrf_token = xsrf_resp.text.strip()

    session.headers.update({
        "accept": "*/*",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "origin": "https://prod.osapiens.cloud",
        "priority": "u=1, i",
        "referer": "https://prod.osapiens.cloud/portal/webbundle/foodplus/field-service-os/supply-chain-portal?app-route-hash=%252Fcertificates",
        "sec-ch-ua": '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
        "x-csrf-token": csrf_token,
    })

    session.cookies.set("SESSION", cookie)

    # producerId = "4063651096873"
    # producerId = "4063651852288"
    # producerId = "7868000709308"
    # producerId = "4063651893021"

    body = (
        b"\x01\x84\x80\xc0>\x18\x08foodplus\x18\x10field-service-os\x18\x18read-certificates-public"
        b"\x19\x15\x00\x1c\x15\x09\x19\x19\x1b\x03\xcc\x00\x15\x00\x18\x07options"
        b"\x19\x19\x00\x15\x09\x19\x19\x1b\x05\xcc\x00\x15\x00\x18\x05query\x19\x19\x00"
        b"\x15\x05\x19\x1a\x1c\x00\x15\x09\x19\x19\x1b\x03\xcc\x00\x15\x00\x18\x03key"
        b"\x19\x19\x00\x15\x05\x19\x1a,\x00\x15\x00\x18\nProducerId\x19\x19\x00\x00\x15"
        b"\x00\x18\rSubProducerId\x19\x19\x00\x19\x00\x00\x15\x00\x18\x05value\x19\x19\x00"
        b"\x15\x00\x18\r00000000\x19\x19\x00\x00\x15\x00\x18\x08operator\x19\x19\x00"
        b"\x15\x0c\x18\x011\x19\x19\x00\x00\x19\x00\x00\x15\x00\x18\x04page\x19\x19\x00"
        b"\x15\x0c\x18\x011\x19\x19\x00\x00\x15\x00\x18\tpageLimit\x19\x19\x00\x15\x0c"
        b"\x18\x0225\x19\x19\x00\x00\x15\x00\x18\x05total\x19\x19\x00\x15\x0c\x18\x010"
        b"\x19\x19\x00\x00\x15\x00\x18\nsortOption\x19\x19\x00\x15\r\x19\x19\x19\x00\x00"
        b"\x00\x15\x00\x18\x0bbookmarkIds\x19\x19\x00\x15\x05\x19\x1a\x00\x19\x00\x00\x15"
        b"\x00\x18\x19isCertificatesByBookmarks\x19\x19\x00\x15\r\x19\x19\x19\x00\x00\x1c"
        b"\x15\x09\x19\x19\x1b\x00\x00\x1c\x15\x09\x19\x19\x1b\x00\x00\x00"
    )
    body = body.replace(b"00000000", producerId.encode())

    resp = session.post(
        "https://prod.osapiens.cloud/portal/rpc",
        data=body,
        timeout=30,
    )

    safe_text = "".join(
        ch if ch >= " " or ch in "\n\r\t" else f"\\x{ord(ch):02x}"
        for ch in resp.text
    )

    # print(safe_text)
    safe_text = safe_text.replace("\r", "")
    safe_text = safe_text.replace("\t", "")
    # print(safe_text)
    clean = re.sub(r"\\x[0-9a-fA-F]{2}", "|", safe_text)

    clean = clean.replace("|||||||\n", "||||||||")
    clean = clean.replace("||||||||", ",")
    clean = clean.replace("|||||||", ":")
    clean = clean.replace("||||||", ":")

    obj = {"producerId":producerId}
    # clean = re.split(r"\\x[0-9a-fA-F]{2}", safe_text)
    # top, bottom = clean.split(",certificates:")

    top, bottom = re.split(r",certificates..", clean)


    top = top.split(",")

    for t in top:
        t = t.replace("|", "")
        t = t.replace("\r", "")
        t = t.replace("\t", "")
        t = t.replace("\n", "")
        t = t.replace("�", "")
        t = t.replace("!", ":")
        if ":" in t and "producerId" not in t:
            key, val = t.split(":")
            obj[key.strip()] = val.strip()

    certs = bottom.split("productAttributes")
    obj["certs"] = {"GRASP":[], "GLOBAL GAP":[]}

    for idx in range(0,len(certs)-1):
        certif_obj = {}
        cert_split = certs[idx].split(",")
        for t in cert_split:
            t = t.replace("|-", ":")
            t = t.replace("|", "")
            t = t.replace("\r", "")
            t = t.replace("\t", "")
            t = t.replace("\n", "")
            t = t.replace("�", "")
            t = t.replace("!", ":")
            t = t.replace("::", ":")
            if ":" in t:
                t = t.replace(":certificateId","certificateId")
                key, val = t.split(":")
                if key != "":
                    val = val.replace("-Integrated","Integrated")
                    val = val.replace("$","")
                    val = val.replace(")","")
                    val = val.replace("(","")
                    certif_obj[key.strip()] = val.strip()
                    if key == "validTo" or key == "lastChange":
                        certif_obj[key.strip()] = datetime.fromtimestamp(int(val.strip())/1000)
        
        if "IFA" in certif_obj["farmAssuranceProduct"]:
            obj["certs"]["GLOBAL GAP"].append(certif_obj)
        elif "GRASP" in certif_obj["farmAssuranceProduct"]:
            obj["certs"]["GRASP"].append(certif_obj)
        

    #only choose the most relevant certs
    if len(obj["certs"]["GLOBAL GAP"]) > 0:
        obj["certs"]["GLOBAL GAP"] = sorted(obj["certs"]["GLOBAL GAP"], key=itemgetter('validTo'))
    if len(obj["certs"]["GRASP"]) > 0:
        obj["certs"]["GRASP"] = sorted(obj["certs"]["GRASP"], key=itemgetter('validTo'))


    best_certs={"GLOBAL GAP":{}, "GRASP":{}}
    now = datetime.now()
    for cert_type in ["GLOBAL GAP", "GRASP"]:
        if len(obj["certs"][cert_type]) > 0:
            last_valid = False
            for idx, cert in enumerate(obj["certs"][cert_type]):

                cert["valid"] = False
                if now <= cert["validTo"]:
                    if cert["status"] == "Certified" or cert["status"] == "Extended":
                        cert["valid"] = True
                if last_valid == False:
                    best_certs[cert_type] = cert
                elif last_valid == True:
                    if cert["valid"] == True:
                        best_certs[cert_type] = cert
                last_valid = cert["valid"]
    obj["certs"]["GLOBAL GAP"] = best_certs["GLOBAL GAP"]
    obj["certs"]["GRASP"] = best_certs["GRASP"]

    #get the country data

    base_link = "https://prod.osapiens.cloud/portal/webbundle/foodplus/field-service-os/supply-chain-portal?app-route-hash=%252Fcertificates%252F"

    if obj["certs"]["GLOBAL GAP"] != {}:
        obj["certs"]["GLOBAL GAP"]["link"] = base_link + obj["certs"]["GLOBAL GAP"]["certificateId"]
        if "CONTROL UNION" in obj["certs"]["GLOBAL GAP"]["certificationBodyName"]:
            obj["certs"]["GLOBAL GAP"]["certificationBodyName"] = "CONTROL UNION"

    if obj["certs"]["GRASP"] != {}:
        obj["certs"]["GRASP"]["link"] = base_link + obj["certs"]["GRASP"]["certificateId"]
        if "CONTROL UNION" in obj["certs"]["GRASP"]["certificationBodyName"]:
            obj["certs"]["GRASP"]["certificationBodyName"] = "CONTROL UNION"

    def build_read_certificate_public_payload(cert_id: str) -> bytes:
        cert = cert_id.encode("ascii")
        if len(cert) >= 128:
            raise ValueError("cert_id too long for simple one-byte length encoding")

        return (
            b"\x01\x84\x80\xc0\x3e"
            b"\x18\x08foodplus"
            b"\x18\x10field-service-os"
            b"\x18\x17read-certificate-public"
            b"\x19\x15\x00\x1c\x15\x09\x19\x19\x1b\x01\xcc\x00\x15\x00"
            b"\x18\x03key"
            b"\x19\x19\x00\x15\x00"
            + b"\x18" + bytes([len(cert)]) + cert +
            b"\x19\x19\x00\x00"
            b"\x1c\x15\x09\x19\x19\x1b\x01\xcc\x00\x15\x00"
            b"\x18\x03key"
            b"\x19\x19\x00\x15\x00"
            + b"\x18" + bytes([len(cert)]) + cert +
            b"\x19\x19\x00\x00"
            b"\x1c\x15\x09\x19\x19\x1b\x00\x00\x00"
        )

    for cert_type in ["GLOBAL GAP"]:
        if obj["certs"][cert_type] != {}:
            if obj["certs"][cert_type]["valid"]:
                cert_id = obj["certs"][cert_type]["certificateId"]
    
                headers = {
                    "accept": "*/*",
                    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
                    "origin": "https://prod.osapiens.cloud",
                    "referer": f"https://prod.osapiens.cloud/portal/webbundle/foodplus/field-service-os/supply-chain-portal?app-route-hash=%252Fcertificates%252F{cert_id}",
                    "x-csrf-token": csrf_token,
                    "content-type": "application/octet-stream",
                }
                
                live_payload = build_read_certificate_public_payload(cert_id)

                resp = session.post(
                    f"{BASE}/portal/rpc",
                    headers=headers,
                    data=live_payload,
                    timeout=30,
                )
                safe_text = "".join(
                    ch if ch >= " " or ch in "\n\r\t" else f"\\x{ord(ch):02x}"
                    for ch in resp.text
                )

                clean = re.sub(r"\\x[0-9a-fA-F]{2}", "|", safe_text)
                clean = clean.split("Countries of destination:one or multiple countries")[1]
                clean = re.split(r"\|\|\|\|\|\|.", clean)[2]
                clean = clean.replace("value", "|")
                clean = clean.replace("|","")
                clean = clean.replace('"',"")
                clean = clean.replace('UNITED STATES',"USA")
                clean = clean.replace('United States',"USA")
                clean = clean.replace('United states',"USA")
                clean = clean.replace('united states',"USA")
                clean = clean.replace('European Union',"EU")
                clean = clean.replace('European union',"EU")
                clean = clean.replace('european union',"EU")
                clean = clean.replace('EUROPEAN UNION',"EU")
                clean = clean.replace(', EC',", ECU")
                clean = clean.replace('EC,',"ECU,")
                clean = clean.replace('ECUADOR',"ECU")
                clean = clean.replace('Ecuador',"ECU")
                clean = clean.replace('ecuador',"ECU")
                clean = clean.strip()
                #convert to three letters for countries
                country_list = country.fetch_countries()
                dest_countries = clean.split(",")

                new_dest_countries = []
                for idx, c in enumerate(dest_countries):
                    c = c.strip()
                    if len(c) > 3:
                        c = c.lower()
                        if country_list[c]["eu"] == True:
                            c = "EU"
                        else:
                            c = country_list[c]["code"]

                    new_dest_countries.append(c)

                new_dest_countries = set(new_dest_countries)
                new_dest_countries = str(new_dest_countries).replace("{","").replace("}","").replace("'",)

                obj["certs"][cert_type]["countries"] = new_dest_countries
            else:
                obj["certs"][cert_type]["countries"] = ""

        if obj["certs"]["GRASP"] != {}:
            obj["certs"]["GRASP"]["countries"] = ""
    return obj


# print(check_ggn_new(4063651893021))