import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from time import sleep, time
import psycopg2
from datetime import datetime, timezone
import GGN_new_db as g


from webdriver_manager.chrome import ChromeDriverManager

def update_database(ggn, expiration_date, certified, countries, level, link, cert_type, tk, output):
    def update_data(DATABASE_URL, ggn, expiration_date, certified, countries, tk, output):
        """ delete part by part id """
        conn = None
        rows_deleted = 0
        response = {"rows_deleted":0, "status":"failed"}
        try:
            # connect to the PostgreSQL database
            conn = psycopg2.connect(DATABASE_URL)
            # create a new cursor
            cur = conn.cursor()
            # execute the UPDATE  statement
            expiration_date_split = ""
            if "/" in expiration_date:
                expiration_date_split = expiration_date.split("/")
            elif "." in expiration_date:
                expiration_date_split = expiration_date.split(".")

            expiration_date = expiration_date_split[2] + "-" + expiration_date_split[1] + "-" + expiration_date_split[0]
            valid = False
            if certified == "Certified":
                valid = True

            #understand if certification exists
            timestamp = datetime.now(timezone.utc)

            sql = "UPDATE certifications SET "
            sql+= "expiration_date = '"+expiration_date+"',"
            sql+= "valid = " + str(valid).upper() + ","
            sql+= "added_by = 'VALIDATOR'," 
            sql+= "added_date = '" + str(timestamp) +"', "
            sql+= "link = '"+link+"', " 
            sql+= "certification_level = '"+level+"',"
            sql+= "certification_countries = '"+countries+"' "
            sql+= "WHERE certification = '"+cert_type+"' AND certification_id = '"+ggn+"'"
            
            print("\n", sql)
            
            cur.execute(sql)
            # output.insert(tk.END, "\n------> Updated farm: " + farm_code_name[count_farms])
            # count_farms += 1

            
            # get the number of updated rows
            response["rows_updated"] = cur.rowcount
            # Commit the changes to the database
            conn.commit()
            # Close communication with the PostgreSQL database
            cur.close()
            response["status"] = "success"
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            response["error"] = str(error)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
        finally:
            if conn is not None:
                conn.close()

        return response
    DATABASE_URL="postgres://u4t3gtm2ajvhpt:pa7e992d29d7eb9d9bf80cfa24ec8294fa327bded0e2626ed8d72a8756202966e@c3l5o0rb2a6o4l.cluster-czz5s0kz4scl.eu-west-1.rds.amazonaws.com:5432/d4osfble0o2rqi"
    res  = update_data(DATABASE_URL, ggn, expiration_date, certified, countries, tk, output)
    if res["status"] == "success":
        output.insert(tk.END, "\n------> Updated in DB")
    else:
        output.insert(tk.END, "\n------> Couldn't update in DB")

def setup(tk, count_output):

    # options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    # options.add_argument('window-size=1920x1080')
    # options.add_argument("disable-gpu")
    # OR options.add_argument("--disable-gpu")

    # count_output.insert(tk.END, "Opening up chrome... ")

    # d = webdriver.Chrome('chromedriver', options=options)
    # d = webdriver.Chrome(options, ChromeDriverManager().install())
    # d = webdriver.Chrome(options=options)

    # count_output.insert(tk.END, "Navigating to global gap... ")
    # d.get("https://database.globalgap.org/globalgap/search/SearchMain.faces?init=1")
    # count_output.insert(tk.END, "Loading website... ")
    # sleep(3)
    
    
    count_output.insert(tk.END, " Ready!")
    return False

def check_ggn_online_new(ggn):
    obj = g.check_ggn_new(ggn)
    level = "independent"
    if obj["isGroupProducer"] == "false":
        level = "association"

    certifications = []
    base_link = "https://prod.osapiens.cloud/portal/webbundle/foodplus/field-service-os/supply-chain-portal?app-route-hash=%252Fcertificates%252F"
    for cert_type in ["GLOBAL GAP", "GRASP"]:
        cert = obj["certs"][cert_type]
        if cert!={}:
            link = cert["link"]
            countries = cert["countries"]
            valid = cert["valid"]
            expiration = cert["validTo"]
            certification_body = cert["certificationBodyName"]
            cert_obj = {"valid":valid, "expires":expiration, "countries":countries, "level":level, "link":link, "certification":cert_type, "certification_body":certification_body}
            certifications.append(cert_obj)
    
    return certifications


def check_ggns(ggn_list_string, tk, count_output, time_output, output):
    #split
    raw_ggn_list = ggn_list_string.split("\n")
    ggn_list = []
    #clean
    for i in raw_ggn_list:
        if i != "":
            ggn_list.append(i)
    elapsed_avg = 0
    elapsed_list = []
    ggn_num = len(ggn_list)-1
    d = ""
    output.delete('1.0', tk.END)
    if len(ggn_list)>0:
        d = setup(tk, count_output)
    else:
        output.insert(tk.END,"Copy GGNs into the list and then run the program.")

    for idx, ggn in enumerate(ggn_list):
        count_output.delete('1.0', tk.END)
        count_output.insert(tk.END, "#"+str(ggn) + " ("+str(idx+1) + "/" + str(ggn_num+1)+")")
        
        if ggn == None:
            continue

        start = time()
        certifs = check_ggn_online_new(ggn)
        output.insert(tk.END, "\n - "+str(ggn))
        for certif in certifs:
            output.insert(tk.END, "\n---> Type: " + str(certif["certification"]) + "\n---> Valid: " + str(certif["valid"]) + "\n---> Expires: " + str(certif["expires"]) + "\n---> Countries: " + str(certif["countries"])  + "\n---> Level: " + str(certif["level"]) + "\n---> Link: " + str(certif["link"]))
            # update_database(ggn, certif["expires"], certif["certified"], certif["countries"], certif["level"], certif["link"], certif["certification"], tk, output)
        end = time()

        elapsed = round(end - start, 0)
        elapsed_list.append(elapsed)
        elapsed_avg = sum(elapsed_list)/len(elapsed_list)
        time_output.delete('1.0', tk.END)
        time_output.insert(tk.END, "Estimated time left: " + str(round(elapsed_avg * (ggn_num - idx)/60, 2)) +" minutes")

