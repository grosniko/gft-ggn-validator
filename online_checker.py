import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from time import sleep, time
import psycopg2
from datetime import datetime, timezone
import GGN_new_db as g
import uuid

from webdriver_manager.chrome import ChromeDriverManager

def update_database(ggn, expiration_date, valid, countries, level, link, cert_type, cert_body, tk, output):
    def update_data(DATABASE_URL, ggn, expiration_date, valid, countries, cert_type, cert_body, tk, output):
        """ delete part by part id """
        conn = None
        rows_deleted = 0
        response = {"rows_deleted":0, "status":"failed"}
        update = True

        try:
            # connect to the PostgreSQL database
            conn = psycopg2.connect(DATABASE_URL)
            # create a new cursor
            cur = conn.cursor()
            response["rows_updated"] = 0
            #check if exists
            timestamp = datetime.now(timezone.utc)

            sql = "SELECT farm_uid FROM certifications "
            sql += "WHERE certification = '"+cert_type+"' "
            sql += "AND certification_id = '"+ggn+"'"

            cur.execute(sql)

            columns = [column[0] for column in cur.description]    
            results = []
            for row in cur.fetchall():
                results.append(dict(zip(columns,row)))

            if len(results) == 0:
                update = False

            if update:
                sql = "UPDATE certifications SET "
                sql+= "expiration_date = '"+expiration_date+"',"
                sql+= "valid = " + str(valid).upper() + ","
                sql+= "added_by = 'VALIDATOR'," 
                sql+= "added_date = '" + str(timestamp) +"', "
                sql+= "link = '"+link+"', " 
                sql+= "certification_level = '"+level+"',"
                # sql+= "certification_countries = '"+countries+"', "
                sql+= "certification_body = '"+cert_body+"' "
                sql+= "WHERE certification = '"+cert_type+"' AND certification_id = '"+ggn+"'"

                cur.execute(sql)
                if cur.rowcount > 0:
                    output.insert(tk.END, "------> Updated in DB!")
                    response["rows_updated"] += cur.rowcount
                    conn.commit()
                else:
                    output.insert(tk.END, "------> Failed to update in DB!")

            if cert_type != "GLOBAL GAP":
                sql = "SELECT certifications.farm_uid,certifications.certification_id, farms.shipper, farms.farm_code, farms.farm_name, farms.association, farms.producer_name  FROM certifications JOIN farms on certifications.farm_uid = farms.uid "
                sql += "WHERE certifications.certification = 'GLOBAL GAP' "
                sql += "AND certifications.certification_id = '"+ggn+"'"

                cur.execute(sql)

                columns = [column[0] for column in cur.description]    
                all_farms = []
                for row in cur.fetchall():
                    all_farms.append(dict(zip(columns,row)))

                #remove the farms that already have a certification
                if update:
                    idxs = []

                    for r in results:
                        for f in all_farms:
                            if f["farm_uid"] == r["farm_uid"]:
                                idxs.append(all_farms.index(f))
                    idxs.sort()
                    idxs.reverse()

                    for i in idxs:
                        del all_farms[i]
      
                if len(all_farms) > 0:
                    for f in all_farms:
                        uid = str(uuid.uuid4())
                        sql = 'INSERT INTO certifications VALUES(\''+uid+'\', \''+f["farm_uid"]+'\', \''+cert_type+'\', \''+ggn+'\', \''+cert_body+'\', NULL, NULL, \''+expiration_date+'\', '+str(valid).upper()+', NULL, \'VALIDATOR\', \''+str(timestamp)+'\', \''+link+'\', \''+level+'\', \'' +countries+'\')'

                        cur.execute(sql)

                        if cur.rowcount == 1:
                            output.insert(tk.END, "------> Added "+cert_type+" to: " +f["shipper"]+" | "+str(f["farm_code"])+"|"+str(f["association"])+"|"+f["farm_name"]+"|"+str(f["producer_name"])+"\n", "added")
                            response["rows_updated"] += 1
                            conn.commit()
                        else:
                            output.insert(tk.END, "------> Failed to add "+cert_type+" to: " +f["shipper"]+" | "+str(f["farm_code"])+"|"+str(f["association"])+"|"+f["farm_name"]+"|"+str(f["producer_name"])+"\n", "add")

            else:
                if not update:
                    output.insert(tk.END, "------> No farms with this GGN in the DB, please add!", 'add')

            
            # Commit the changes to the database
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

        if response["status"] != "success":
            output.insert(tk.END, "------> Couldn't update DB...")

        return response
    DATABASE_URL="postgres://u4t3gtm2ajvhpt:pa7e992d29d7eb9d9bf80cfa24ec8294fa327bded0e2626ed8d72a8756202966e@c3l5o0rb2a6o4l.cluster-czz5s0kz4scl.eu-west-1.rds.amazonaws.com:5432/d4osfble0o2rqi"
    res = update_data(DATABASE_URL, ggn, expiration_date, valid, countries, cert_type, cert_body, tk, output)

    return res
    

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
    if obj == False:
        certifications = False
    else:
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
                expiration = str(cert["validTo"]).split(" ")[0]
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
        if certifs == False:
            output.insert(tk.END, "\n------------\n\n - "+str(ggn)+" - BAD GGN!", "add")
        else:
            output.insert(tk.END, "\n------------\n\n - "+str(ggn))
            for certif in certifs:
                output.insert(tk.END, "\n\n---> Type: " + str(certif["certification"]) + "\n---> Valid: " + str(certif["valid"]) + "\n---> Expires: " + str(certif["expires"]) + "\n---> Countries: " + str(certif["countries"])  + "\n---> Level: " + str(certif["level"]) + "\n---> Certifier: " + str(certif["certification_body"]) + "\n---> Link: " + str(certif["link"])+"\n")
                update_database(ggn, certif["expires"], certif["valid"], certif["countries"], certif["level"], certif["link"], certif["certification"], certif["certification_body"], tk, output)
                output.see(tk.END)
        end = time()

        elapsed = round(end - start, 0)
        elapsed_list.append(elapsed)
        elapsed_avg = sum(elapsed_list)/len(elapsed_list)
        time_output.delete('1.0', tk.END)
        time_output.insert(tk.END, "Estimated time left: " + str(round(elapsed_avg * (ggn_num - idx)/60, 2)) +" minutes")

