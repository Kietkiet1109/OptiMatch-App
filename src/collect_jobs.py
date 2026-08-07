import requests
from bs4 import BeautifulSoup
import pandas as pd
import shelve

url = 'https://www.themuse.com/api/public/jobs'
datafile = '../data/raw/jobs.shelf'
outputfile = '../data/raw/jobs.csv'

# Define number of jobs to collect
category_target = 75

# Define Computer Science job categories
categories = [
    'Computer and IT',
    'Data and Analytics',
    'Software Engineering',
    'Science and Engineering'
]

# Keep track of jobs already collected
seen_ids = set()

# Create lists for job records
job_id = []
job_title = []
company = []
category = []
job_level = []
location = []
description = []
publication_date = []
job_url = []


with shelve.open(datafile, 'n') as data:

    # Request jobs from each category
    for current_category in categories:
        page = 0
        page_count = 1
        num_job = 0

        # Continue requesting pages until the target is reached
        while page < page_count and num_job < category_target:
            # Fetches job records from the API
            params = {'page': page, 'category': current_category, 'descending': 'true'}
            response = requests.get(url, params = params, timeout = 30)

            if response.status_code != 200:
                raise Exception('Cannot collect jobs')

            result = response.json()

            page_count = result.get('page_count', 0)
            jobs = result.get('results', [])

            for job in jobs:

                # Get all categories for the job
                category_names = list()
                for category_item in job.get('categories', []):
                    category_names.append(category_item.get('name', ''))

                # Keep only jobs from the requested category
                if current_category not in category_names:
                    continue

                # Skip all job that have no job id
                current_job_id = str(job.get('id', ''))
                if current_job_id == '':
                    continue
                if current_job_id in seen_ids:
                    continue

                # Get the job title
                current_title = job.get('name', '')

                # Get the company name
                companies = job.get('company', {})
                current_company = companies.get('name', '')

                # Get all job locations
                current_locations = []
                for location_item in job.get('locations', []):
                    location_name = location_item.get('name', '')
                    if location_name != '':
                        current_locations.append(location_name)
                current_location = ' | '.join(current_locations)

                # Get all experience levels
                current_levels = []
                for level_item in job.get('levels', []):
                    level_name = level_item.get('name', '')
                    if level_name != '':
                        current_levels.append(level_name)
                current_level = ' | '.join(current_levels)

                # Get and convert the HTML description
                html_description = job.get('contents', '')
                soup = BeautifulSoup(html_description, 'html.parser')
                current_description = soup.get_text(' ', strip=True)

                # Get the publication date
                current_publication_date = job.get('publication_date', '')

                # Get the public job page URL
                refs = job.get('refs', {})
                current_job_url = refs.get('landing_page', '')

                # Store raw job data
                key = f'job_{current_job_id}'
                data[key] = {
                    'job_id': current_job_id,
                    'job_title': current_title,
                    'company': current_company,
                    'category': current_category,
                    'job_level': current_level,
                    'location': current_location,
                    'description': current_description,
                    'publication_date': current_publication_date,
                    'job_url': current_job_url
                }

                # Mark job as collected
                seen_ids.add(current_job_id)
                num_job += 1

                # Stop after collecting enough number of jobs for each category
                if num_job >= category_target:
                    break

            # Go to the next page
            page += 1


# Read job records from the shelf
with shelve.open(datafile, 'r') as data:

    for k, v in data.items():
        job_id.append(v['job_id'])
        job_title.append(v['job_title'])
        company.append(v['company'])
        category.append(v['category'])
        job_level.append(v['job_level'])
        location.append(v['location'])
        description.append(v['description'])
        publication_date.append(v['publication_date'])
        job_url.append(v['job_url'])


# Convert job data to dataframe
jobs = pd.DataFrame(
    {
        'job_id': job_id,
        'job_title': job_title,
        'company': company,
        'category': category,
        'job_level': job_level,
        'location': location,
        'description': description,
        'publication_date': publication_date,
        'job_url': job_url,
    }
)

# Save raw scraped job data
jobs.to_csv(outputfile, index = False)
