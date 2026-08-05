import requests
from bs4 import BeautifulSoup
import pandas as pd
import shelve


url = "https://www.sfu.ca/students/calendar/2026/fall/courses/cmpt.html"

datafile = "../data/raw/courses.shelf"
outputfile = "../data/raw/courses.csv"

course_num = []
course_name = []
description = []


# Get HTML page
response = requests.get(url)

if response.status_code != 200:
    raise Exception("Cannot access SFU course page")

soup = BeautifulSoup(response.text, "html.parser")

# Find all course blocks by h3-tag
courses = soup.find_all("h3")

with shelve.open(datafile, "c") as data:
    for course in courses:
        title = course.get_text(strip=True)

        # Collect only CMPT courses
        if not title.startswith("CMPT"):
            continue

        # Get description from the following p-tag
        description_tag = course.find_next("p")

        if description_tag:
            desc = description_tag.get_text(strip=True)
        else:
            desc = ""


        # Split course number and course name
        parts = title.split("- ", 1)


        if len(parts) == 2:
            number = parts[0]
            name = parts[1]

        else:
            number = title
            name = ""

        # Store raw data
        key = number.replace(" ", "_")

        data[key] = {
            "course_num": number,
            "course_name": name,
            "description": desc,
        }

# Read data back from shelf
with shelve.open(datafile, "r") as data:

    for k, v in data.items():
        course_num.append(v["course_num"])
        course_name.append(v["course_name"])
        description.append(v["description"])

# Convert to dataframe
courses = pd.DataFrame({
        "course_num": course_num,
        "course_name": course_name,
        "description": description
    }
)

# Save scraped data
courses.to_csv(outputfile, index = False)
