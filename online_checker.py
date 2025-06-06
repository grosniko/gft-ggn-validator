import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from time import sleep, time
import psycopg2


from webdriver_manager.chrome import ChromeDriverManager

def update_database(ggn, expiration_date, certified, countries, tk, output):
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
            if certified == "Yes" or certified == "Sí":
                valid = True

            sql = "UPDATE certifications "
            sql += "SET expiration_date = '" + str(expiration_date) + "'"
            if expiration_date != "not found":
                sql += ", valid = " + str(valid).upper() + " "
            if countries != "not found":
                sql += ", certification_countries = '" + str(countries).upper() + "' "
            sql += "FROM farms "
            sql += "WHERE farms.uid::VARCHAR(255) = certifications.farm_uid::VARCHAR(255) "
            sql += "AND farms.ggn = '" + ggn + "' "
            sql += "AND certifications.certification_id = '" + ggn + "' "
            
            cur.execute(sql)
            
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
        output.insert(tk.END, " ---> Updated in DB")
    else:
        output.insert(tk.END, " ---> Couldn't update in DB")

def setup(tk, count_output):

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    # options.add_argument('window-size=1920x1080')
    # options.add_argument("disable-gpu")
    # OR options.add_argument("--disable-gpu")

    count_output.insert(tk.END, "Opening up chrome... ")

    # d = webdriver.Chrome('chromedriver', options=options)
    # d = webdriver.Chrome(options, ChromeDriverManager().install())
    d = webdriver.Chrome(options=options)

    count_output.insert(tk.END, "Navigating to global gap... ")
    d.get("https://database.globalgap.org/globalgap/search/SearchMain.faces?init=1")
    count_output.insert(tk.END, "Loading website... ")
    sleep(3)
    
    
    count_output.insert(tk.END, " Ready!")
    return d

def check_ggn_online(d, ggn):

    # print("identifying search box and query button...")
    # ggn_box = d.find_element('id', 'content:search:searchFilterTile:_idJsp138')
    # button = d.find_element('id', 'content:search:searchFilterTile:enterPressedButton')


    # print("Querying for", ggn)
    # ggn_box.clear()
    # ggn_box.send_keys(ggn)
    # button.click()
    # ggn_box.send_keys(Keys.RETURN)

    d.get("https://database.globalgap.org/globalgap/search/SearchMain.faces?searchQuery="+str(ggn))

    cell_name = "searchTdBorderLeftBorderBottom"
    heading_name = "searchHeadlineProduct searchTdBorderLeft"

    heading = "Certified/assessed process"
    certif = "not found/no"
    countries = "not found/none"
    expiration = "not found/none"
    try:
        # items = d.find_elements("class name", "searchTdBorderLeftBorderBottom")
        items = d.find_elements(By.XPATH, "/html/body/div[2]/div[2]/div/form/div[7]/div/table/tbody/tr[8]/td[10]/table/tbody/tr/td/table/tbody/tr/td")
        
        # style = "min-width: 110px; font-weight: bold; color: green; width: 110px;"

        #cell number
        certif = 5
        expiration = 6
        countries = 10
        link = 11

        count = 1
        for i in items:
           
            if count == certif:
                certif = i.text
                # print(count, i.text)
                continue
            if count == expiration:
                expiration = i.text
                # print(count, i.text)
                continue
            if count == countries:
                countries = i.text
                # print(count, i.text)
                continue
            # if count == link: doesnt work in global gap site
            #     link = i.text.split("|")[1]
            #     print(link)
            #     print(count, link)
            #     continue
            count += 1

        # print(certif, expiration, countries)
        #link = items[12-1].innerHTML.split("|")[0]
        # for i in items:

            # s = i.get_attribute("style")
            # if s == style:
            #     certif = i.get_attribute("innerHTML")
            #     break
        # print("Done.")
    except Exception as e:
        print("Error:", str(e))

    # expiration = "not found"

    # try:
    #     items = d.find_elements("class name", "searchTdBorderLeftBorderBottom")

    #     style = "min-width: 120px; width: 120px;"
    #     index = 2
    #     start = 0
    #     for i in items:

    #         s = i.get_attribute("style")
    #         if s == style:

    #             if start == index:
    #                 expiration = i.get_attribute("innerHTML")
    #                 break
    #             start += 1

    #     # print("Done.")
    # except Exception as e:
    #     print("Error:", str(e))

    return {"certified":certif, "expires":expiration, "countries":countries}

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
        certif = check_ggn_online(d, ggn)
        output.insert(tk.END, "\n"+str(ggn) + " ---> " + str(certif["certified"]) + " ---> Expires on " + str(certif["expires"]) + " ---> Countries:" + str(certif["countries"]))
        
        update_database(ggn, certif["expires"], certif["certified"], certif["countries"], tk, output)
        end = time()

        elapsed = round(end - start, 0)
        elapsed_list.append(elapsed)
        elapsed_avg = sum(elapsed_list)/len(elapsed_list)
        time_output.delete('1.0', tk.END)
        time_output.insert(tk.END, "Estimated time left: " + str(round(elapsed_avg * (ggn_num - idx)/60, 2)) +" minutes")