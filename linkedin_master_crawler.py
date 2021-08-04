from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import os
import sys
import json
import parameters

class LinkdinScraper:
    def __init__(self, url,keywords=None,domain=None,location=None,choice=None):
        options = webdriver.ChromeOptions()
        # options.add_argument('--disable-gpu')
        # options.add_argument('--no-sandbox')
        # options.add_argument('--headless')
        self.driver = webdriver.Chrome(executable_path=r"chromedriver.exe",options = options)
        self.driver.get('https://www.linkedin.com')

        username = self.driver.find_element_by_id('session_key')
        username.send_keys(parameters.linkedin_username)
        time.sleep(0.5)

        password = self.driver.find_element_by_id('session_password')
        password.send_keys(parameters.linkedin_password)
        time.sleep(0.5)

        sign_in_button = self.driver.find_element_by_class_name('sign-in-form__submit-button')
        sign_in_button.click()
        keywords = keywords.replace(" ","%20")
        if choice == 'jobs' :
            self.url = url + '?keyword=' + keywords + "?location=" + location
        elif choice == "people" :
            self.url = url
            # self.url = url + '?keyword=' + keywords + "&location=" + location
        self.domain = domain
        self.location = location

    def remove_spaces(self,spaces):
        spaces = spaces.strip().replace(" +","")
        spaces = " ".join(spaces.split())
        return spaces

    def scroll(self):
        print(self.url)
        self.driver.get(self.url)

        SCROLL_PAUSE_TIME = 2
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        print(last_height)
        while True:
            content = self.driver.page_source
            soup = BeautifulSoup(content, "html.parser")
            st_divs1 = soup.find_all('div',{"class" : "base-card base-card--link base-search-card base-search-card--link job-search-card"})
            print(len(st_divs1))

            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE_TIME)

            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        return st_divs1

    def scrape_job_mod(self) :

        st_divs1 = []
        data = []

        START_PAGES = 0
        JOBID = ""
        TITLE = ""
        COMPANY = ""
        LOCATION = ""
        LINK = ""
        DESCRIPTION = ""
        JOB_TYPE= ""
 
        try:
            url_start = self.url + f'&start={START_PAGES}'
            print(url_start)
            self.driver.get(url_start)
            time.sleep(1)
            content = self.driver.page_source
            soup = BeautifulSoup(content, "html.parser")
            st_divs1 += soup.find_all('li',{"class" : "jobs-search-results__list-item occludable-update p0 relative ember-view"})
            st_divs1 += soup.find_all('li',{"class" : "jobs-search-results__list-item occludable-update p0 relative jobs-search-results__job-card-search--generic-occludable-area ember-view"})
            # print(st_divs1)
            print(len(st_divs1))
        except Exception as e : 
            print(e)
            print("No more data available !!!")
            flag_end = 1

        while True :
            a = input(f"Length of Data List {len(st_divs1)} . Do you want to continue Scraping ??? --> ")
            if a == 'y':  
                START_PAGES += 25
                try:
                    url_start = self.url + f'&start={START_PAGES}'
                    print(url_start)
                    self.driver.get(url_start)
                    content = self.driver.page_source
                    soup = BeautifulSoup(content, "html.parser")
                    st_divs1 += soup.find_all('li',{"class" : "jobs-search-results__list-item occludable-update p0 relative ember-view"})
                    st_divs1 += soup.find_all('li',{"class" : "jobs-search-results__list-item occludable-update p0 relative jobs-search-results__job-card-search--generic-occludable-area ember-view"})
                    print(len(st_divs1))
                except Exception as e : 
                    print(e)
                    print("No more data available !!!")
                    flag_end =1
                    break
            elif a == 'n' :
                break 

        for st_div_item in st_divs1 :

            print("*"*20)
            job_id = st_div_item['data-occludable-entity-urn'].split(':')[-1]
            print(job_id)
            JOBID = job_id

            links = f'https://www.linkedin.com/jobs/view/{job_id}/'
            LINK = links

            self.driver.get(links)
            time.sleep(2)
            content = self.driver.page_source
            soup_1 = BeautifulSoup(content, "html.parser")

            try :
                title = self.remove_spaces(soup_1.find('h1',{"class" : "t-24 t-bold"}).text)
                print(title)
                TITLE = title

                company = self.remove_spaces(soup_1.find('a',{"class" : "ember-view t-black t-normal"}).text)
                print(company)
                COMPANY = company

                location = self.remove_spaces(soup_1.find('span',{"class" : "jobs-unified-top-card__bullet"}).text)
                print(location)
                LOCATION = location

                job_type = self.remove_spaces(soup_1.find('div',{"class" : "jobs-unified-top-card__job-insight"}).text)
                print(job_type)
                JOB_TYPE = job_type

                job_description = self.remove_spaces(soup_1.find('div',{"class" : "jobs-box__html-content jobs-description-content__text t-14 t-normal"}).text)
                print(job_description)
                DESCRIPTION = job_description

                scraper_data = {}
                scraper_data['job_id'] = JOBID
                scraper_data['title'] = TITLE
                scraper_data['company'] = COMPANY
                scraper_data['location'] = LOCATION
                scraper_data['link'] = LINK
                scraper_data['description'] = DESCRIPTION
                scraper_data['job_type'] = JOB_TYPE
                data.append(scraper_data)
            
            except Exception as e : 
                print(e)
                pass

            with open(f'linkedin_jobs_mod_{self.domain}_{self.location}.json','w',encoding='utf8') as file :
                json.dump(data,file,ensure_ascii=False, indent=1)

        if data == [] :
            raise Exception('The data object is empty . Please run the Python File once again ')

        self.driver.quit()
    def scrape_job(self):

        data = []
        st_divs1 = []
        st_divs1 = self.scroll()

        for divs in st_divs1 :
            print("*"*20)

            JOBID = ""
            TITLE = ""
            COMPANY = ""
            PLACE = ""
            DATE = ""
            LINK = ""
            DESCRIPTION = ""
            JOB_FUNCTION = ""
            EMPLOYMENT_TYPE = ""
            INDUSTRIES = ""

            job_id = divs['data-entity-urn'].split(':')[-1]
            job_id = self.remove_spaces(job_id)
            print(job_id)
            JOBID = job_id

            links = divs.find('a',{"class" :"base-card__full-link"})['href']
            links = self.remove_spaces(links)
            print(links)
            LINK = links

            title = divs.find('h3',{"class" : "base-search-card__title"}).text
            title = self.remove_spaces(title)
            print(title)
            TITLE = title

            company = divs.find('h4',{"class" : "base-search-card__subtitle"}).text
            company = self.remove_spaces(company)
            print(company)
            COMPANY = company

            location = divs.find('span',{"class" : "job-search-card__location"}).text
            location = self.remove_spaces(location)
            print(location)
            PLACE = location

            try :
                date_time = divs.find('time',{"class" : "job-search-card__listdate--new"})['datetime']
                date_time = self.remove_spaces(date_time)
                print(date_time)
                DATE = date_time

            except Exception as e :
                print(e)
                pass


            self.driver.get(links)
            content = self.driver.page_source
            soup_1 = BeautifulSoup(content, "html.parser")
            time.sleep(3)
            
            try :
                description = soup_1.find('div',{"class" : "show-more-less-html__markup"}).text
                description = self.remove_spaces(description)
                print(description)
                DESCRIPTION = description

            except Exception as e :
                print(e)
                pass

            try :
                info_div = soup_1.find_all('li',{"class" : "description__job-criteria-item"})
                for info in info_div :
                    employment_type = self.remove_spaces(info.find('h3').text)
                    employment_desc = self.remove_spaces(info.find('span').text)
                    print(employment_type,employment_desc)
                    if 'employment' in employment_type.lower() :
                        EMPLOYMENT_TYPE = employment_desc
                    elif 'job' in employment_type.lower() :
                        JOB_FUNCTION = employment_desc
                    elif 'industries' in employment_type.lower() :
                        INDUSTRIES = employment_desc

            except Exception as e:
                print(e)
                pass

            scraper_data = {}
            scraper_data['job_id'] = JOBID
            scraper_data['title'] = TITLE
            scraper_data['company'] = COMPANY
            scraper_data['place'] = PLACE
            scraper_data['date'] = DATE
            scraper_data['link'] = LINK
            scraper_data['description'] = DESCRIPTION
            scraper_data['job_function'] = JOB_FUNCTION
            scraper_data['employment_type'] = EMPLOYMENT_TYPE
            scraper_data['industries'] = INDUSTRIES
            data.append(scraper_data)

            with open(f'linkedin_jobs_{self.domain}_{self.location}.json','w',encoding='utf8') as file :
                json.dump(data,file,ensure_ascii=False, indent=1)

        if data == [] :
            raise Exception('The data object is empty . Please run the Python File once again ')

        self.driver.quit()
    
    def scrape_people_mod(self):
        print(self.url)

        START_PAGES = 1
        data = []
        PROFILE_LINK = ""
        GOOGLE_INFO = ""
        NAME = ""
        INFO = ""
        LOCATION = ""
        COMPANY = ""
        CONNECTIONS = ""
        ABOUT = ""

        self.driver.get(self.url)
        time.sleep(1)
        content = self.driver.page_source
        soup = BeautifulSoup(content, "html.parser")
        soup_title = soup.find_all('li',{"class" :"reusable-search__result-container"})

        while True :
            a = input(f"Length of Data List {len(soup_title)} . Do you want to continue Scraping ??? --> ")
            if a == 'y':  
                START_PAGES += 1
                try:
                    url_start = self.url + f'&page={START_PAGES}'
                    print(url_start)
                    self.driver.get(url_start)
                    content = self.driver.page_source
                    soup = BeautifulSoup(content, "html.parser")
                    soup_title += soup.find_all('li',{"class" : "reusable-search__result-container"})
                    print(len(soup_title))
                except Exception as e : 
                    print(e)
                    print("No more data available !!!")
                    flag_end =1
                    break
            elif a == 'n' :
                break 

        for title_item in soup_title :
            title = self.remove_spaces(title_item.find('span',{"class" :"entity-result__title-text t-16"}).text)
            print(title)
            if title.lower() != 'linkedin member' :
                links = title_item.find('a')['href']
                print(links)
                PROFILE_LINK = links

                self.driver.get(links)
                time.sleep(2)
                content_linkedin = self.driver.page_source
                soup_linkedin = BeautifulSoup(content_linkedin, "html.parser")
                div_info = soup_linkedin.find('div',{"class" :"ph5 pb5"})

                if div_info == None :
                    div_info = soup_linkedin.find('div',{"class" :"ph5"})

                try :
                    try :
                        name = self.remove_spaces(div_info.find('h1',{'class':'text-heading-xlarge inline t-24 v-align-middle break-words'}).text)
                        print(name)
                        NAME = name
                    except :
                        pass

                    try :
                        info = self.remove_spaces(div_info.find('div',{'class':'text-body-medium break-words'}).text)
                        print(info)
                        INFO = info
                    except :
                        pass

                    try :    
                        location = self.remove_spaces(div_info.find('div',{'class':'pb2'}).text)
                        print(location)
                        LOCATION = location
                    except :
                        pass

                    try :
                        company = self.remove_spaces(div_info.find('ul',{'class':'pv-text-details__right-panel'}).text)
                        print(company)
                        COMPANY = company
                    except :
                        pass

                    try:    
                        connections = self.remove_spaces(div_info.find('ul',{'class':'pv-top-card--list pv-top-card--list-bullet display-flex pb1'}).text)
                        print(connections)
                        CONNECTIONS = connections
                    except :
                        pass
                        
                    try:
                        about = self.remove_spaces(soup_linkedin.find('div',{'class':'pv-oc ember-view'}).find('div').text)
                        print(about)
                        ABOUT = about
                    except :
                        pass
                    
                    contact_info_link = soup_linkedin.find('a',{'class':'ember-view link-without-visited-state cursor-pointer text-heading-small inline-block break-words'})['href']
                    contact_info_link = 'https://www.linkedin.com/' + contact_info_link
                    self.driver.get(contact_info_link)
                    content_contact_info = self.driver.page_source
                    soup_contact_info = BeautifulSoup(content_contact_info, "html.parser")
                    div_contact_info = soup_contact_info.find('div',{"class" :"pv-profile-section__section-info section-info"})
                    CONTACT_INFO = self.remove_spaces(div_contact_info.text)
                    print(CONTACT_INFO)

                    scraper_data = {}
                    scraper_data['profile_link'] = PROFILE_LINK
                    scraper_data['name'] = NAME
                    scraper_data['information'] = INFO
                    scraper_data['location'] = LOCATION
                    scraper_data['company'] = COMPANY
                    scraper_data['connections'] = CONNECTIONS
                    scraper_data['about'] = ABOUT
                    scraper_data['contact_info'] = CONTACT_INFO
                    data.append(scraper_data)
                except :
                    pass

                with open(f'linkedin_people_mod_{self.domain}_{self.location}.json','w',encoding='utf8') as file :
                    json.dump(data,file,ensure_ascii=False, indent=1)

        if data == [] :
            raise Exception('The data object is empty . Please run the Python File once again ')
        self.driver.quit()


    def scrape_people(self) :

        print(self.url)

        data = []
        PROFILE_LINK = ""
        GOOGLE_INFO = ""
        NAME = ""
        INFO = ""
        LOCATION = ""
        COMPANY = ""
        CONNECTIONS = ""
        ABOUT = ""

        self.driver.get(self.url)
        content = self.driver.page_source
        soup = BeautifulSoup(content, "html.parser")
        links = soup.find_all('div',{"class" :"yuRUbf"})

        while True : 
            a = input(f"Length of Data List {len(links)} . Do you want to continue Scraping ??? --> ")
            if a == 'y': 
                try : 
                    next_button = self.driver.find_element_by_id('pnnext')
                    next_button.click()
                    time.sleep(0.5)
                except : 
                    print("No more data available !!!")
                    break

                self.driver.get(self.driver.current_url)
                content = self.driver.page_source
                soup = BeautifulSoup(content, "html.parser")
                links += soup.find_all('div',{"class" :"yuRUbf"})
            elif a == 'n' :
                break

        for link in links :
            print("*"*20)
            key_name = link.find('h3',{'class':'LC20lb DKV0Md'}).text
            print(key_name)
            GOOGLE_INFO = key_name

            profile_link = link.find('a')['href']
            print(profile_link) 
            PROFILE_LINK = profile_link

            self.driver.get(profile_link)
            time.sleep(2)
            content_linkedin = self.driver.page_source
            soup_linkedin = BeautifulSoup(content_linkedin, "html.parser")
            div_info = soup_linkedin.find('div',{"class" :"ph5 pb5"})

            if div_info == None :
                div_info = soup_linkedin.find('div',{"class" :"ph5"})

            try :
                name = self.remove_spaces(div_info.find('h1',{'class':'text-heading-xlarge inline t-24 v-align-middle break-words'}).text)
                print(name)
                NAME = name
            except :
                pass

            try :
                info = self.remove_spaces(div_info.find('div',{'class':'text-body-medium break-words'}).text)
                print(info)
                INFO = info
            except :
                pass

            try :    
                location = self.remove_spaces(div_info.find('div',{'class':'pb2'}).text)
                print(location)
                LOCATION = location
            except :
                pass

            try :
                company = self.remove_spaces(div_info.find('ul',{'class':'pv-text-details__right-panel'}).text)
                print(company)
                COMPANY = company
            except :
                pass

            try:    
                connections = self.remove_spaces(div_info.find('ul',{'class':'pv-top-card--list pv-top-card--list-bullet display-flex pb1'}).text)
                print(connections)
                CONNECTIONS = connections
            except :
                pass
                
            try:
                about = self.remove_spaces(soup_linkedin.find('div',{'class':'pv-oc ember-view'}).find('div').text)
                print(about)
                ABOUT = about
            except :
                pass
            
            try :
                contact_info_link = soup_linkedin.find('a',{'class':'ember-view link-without-visited-state cursor-pointer text-heading-small inline-block break-words'})['href']
                contact_info_link = 'https://www.linkedin.com/' + contact_info_link
                self.driver.get(contact_info_link)
                content_contact_info = self.driver.page_source
                soup_contact_info = BeautifulSoup(content_contact_info, "html.parser")
                div_contact_info = soup_contact_info.find('div',{"class" :"pv-profile-section__section-info section-info"})
                CONTACT_INFO = self.remove_spaces(div_contact_info.text)
                print(CONTACT_INFO)
            except:
                pass

            scraper_data = {}
            scraper_data['google_info'] = GOOGLE_INFO
            scraper_data['profile_link'] = PROFILE_LINK
            scraper_data['name'] = NAME
            scraper_data['information'] = INFO
            scraper_data['location'] = LOCATION
            scraper_data['company'] = COMPANY
            scraper_data['connections'] = CONNECTIONS
            scraper_data['about'] = ABOUT
            scraper_data['contact_info'] = CONTACT_INFO
            data.append(scraper_data)

            with open(f'linkedin_people_{self.domain}_{self.location}.json','w',encoding='utf8') as file :
                json.dump(data,file,ensure_ascii=False, indent=1)

        if data == [] :
            raise Exception('The data object is empty . Please run the Python File once again ')
        self.driver.quit()

if __name__ == '__main__' :
    
    location_dict = {'United states' : '103644278',
                     'Singapore' : '102454443',
                     'Malaysia' : '106808692',
                     'India' : '102713980',
                    }
    choice = 'people'
    location = "India"
    if choice == "jobs" :
        domain = "testing agency"
        url ="https://www.linkedin.com/jobs/search/"
        keywords = domain + ' ' +location 
        obj = LinkdinScraper(url,keywords,domain,location,choice)
        obj.scrape_job_mod()
    elif choice == "people" :
        domain = "Ott development"
        url = f"https://www.linkedin.com/search/results/people/?geoUrn={location_dict['India']}&keywords=ott%20development"
        # url ="https://www.google.com/search?q=site%3Alinkedin.com%2Fin%2F"
        keywords_all = "AND" + domain + "AND" + location
        obj = LinkdinScraper(url,keywords_all,domain,location,choice)
        obj.scrape_people_mod()
    
