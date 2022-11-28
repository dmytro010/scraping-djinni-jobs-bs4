from bs4 import BeautifulSoup
import requests
from datetime import date, timedelta
import json


class ParseDjinni():
    def __init__(self, keyword:str, filename:str):
        self.keyword = keyword 
        self.filename = filename 
        self.job_count = 0
        self.jobs_dict = {}
    
    def parse_jobs_list(self, page=1)-> dict:
        
        link = f'https://djinni.co/jobs/?keywords={self.keyword}&page={page}'
        
        r = requests.get(link)
        r.raise_for_status()

        html_text = r.text
        soup = BeautifulSoup(html_text, 'lxml')
        next_page = soup.find('a', class_='btn btn-lg btn-primary')['href'].split("page=")[-1]\
            if soup.find('a', class_='btn btn-lg btn-primary') else None
        jobs = soup.find_all('li', class_='list-jobs__item list__item')

        for job in jobs:
            job_dict = {}
            self.job_count += 1 
            parsed_link = job.find('a', class_='profile')['href']
            job_link = f'https://djinni.co{parsed_link}'
            job_title = job.find('a', class_='profile').span.text.strip()
            parsed_date = job.find('div', class_='text-date') \
                .text.strip().replace('\n', ',').split(",")[0]
            salary = job.find('span', class_='public-salary-item').text\
                if job.find('span', class_='public-salary-item') else "not specified"
            company_name = job.find('div', class_='list-jobs__details__info')\
                .a.text.strip()

            job_date = None
            if parsed_date == 'сьогодні':
                job_date = date.today()
            elif parsed_date == 'вчора':
                job_date = date.today() - timedelta(days=1)
            else:
                job_date = parsed_date
            
            job_skills, job_replies, job_views = self.parse_single_job_info(job_link=job_link)
            job_dict = {
                'job_title': job_title,
                'company': company_name,
                'date': str(job_date),
                'salary': salary,
                'link': job_link,
                'skills': job_skills,
                'views': job_views,
                'replies': job_replies }
        
            self.jobs_dict.update({self.job_count: job_dict})
            
        if next_page != None:
            self.parse_jobs_list(page=next_page)
        else:
            with open(f'./{self.filename}.json', "w") as f:
                json.dump(self.jobs_dict, f)
            

    def parse_single_job_info(self, job_link:str)->list:
        r = requests.get(job_link)
        r.raise_for_status()
        job_text = r.text
        job_soup = BeautifulSoup(job_text, 'lxml')
        views_section = job_soup.find('div', class_='profile-page-section text-small')
        card = job_soup.find('div', class_='card job-additional-info')
        skills = card.find_all('li')[1]\
            .text.strip().replace('\n', '').replace(" ", "").split(",")
        job_replies = views_section.find('p')\
            .text.strip().replace("\n", ",").split(", ")[5]
        job_views = views_section.find('p')\
            .text.strip().replace("\n", ",").split(", ")[-1]

        return [skills, job_replies, job_views]

if __name__ == '__main__':
    parse = ParseDjinni(keyword='django', filename='djinni_django_jobs')
    parse.parse_jobs_list()


