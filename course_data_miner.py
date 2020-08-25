import requests
from bs4 import BeautifulSoup
import json
import re
import pickle
import csv
import os
from tqdm import tqdm
from course_data_info import *


def write_to_csv(path, data):
    """
    Write given course data to a CSV file with given path.
    :param path: Path to create new CSV file
    :param data: An array of dictionary of course data
    :return: None
    """
    with open(path, 'w') as csvfile:
        fieldnames = ["Code", "Title", "Prerequisites", "Corequisites", "Exclusions"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def mine_utsg_courses():
    """
    Mine UTSG course data.
    :return: None
    """
    st_george_api_url = "https://timetable.iit.artsci.utoronto.ca/api/20209/courses?org="

    course_data = {}

    for subject in tqdm(st_george_subjects, desc="UTSG"):
        request_url = st_george_api_url + subject
        results = json.loads(requests.get(request_url).text)

        for key in results:

            course_code = results[key]['code']

            if course_code in course_data:
                continue

            course_title = results[key]['courseTitle']
            course_description = BeautifulSoup(results[key]['courseDescription'], 'html5lib').text.strip()
            exclusions = results[key]['exclusion']
            prerequisites = results[key]['prerequisite']
            corequisites = results[key]['corequisite']

            course_data[course_code] = {"Title": course_title,
                                        "Description": course_description,
                                        "Exclusions": exclusions,
                                        "Prerequisites": prerequisites,
                                        "Corequisites": corequisites}

    with open('./data/utsg_courses.pickle', 'wb') as handle:
        pickle.dump(course_data, handle, protocol=pickle.HIGHEST_PROTOCOL)


def mine_utsc_courses():
    """
    Mine UTSC course data.
    :return: None
    """
    utsc_api_url = "https://www.utsc.utoronto.ca/regoffice/timetable/view/api.php"
    utsc_course_look_up_url = "https://utsc.calendar.utoronto.ca/course/"

    course_data = {}

    for i in tqdm(range(2, utsc_max_subjects + 1), desc="UTSC"):
        results = json.loads(requests.post(utsc_api_url, data={"departments[]": str(i)}).text)

        for course in results[0]:
            course_code = results[0][course]['course_cd']

            if course_code in course_data:
                continue

            course_title = results[0][course]['title']

            course_url = utsc_course_look_up_url + course_code
            response = requests.get(course_url).text
            soup = BeautifulSoup(response, 'html5lib')

            description = soup.find("div",
                                    class_="field field-name-body field-type-text-with-summary field-label-hidden")

            if description:
                description = description.text.strip()

            prerequisites = soup.find("div", text=re.compile("Prerequisite:"))
            corequisites = soup.find("div", text=re.compile("Corequisite:"))
            exclusions = soup.find("div", text=re.compile("Exclusion:"))

            if prerequisites:
                prerequisites = prerequisites.next_sibling.text

            if corequisites:
                corequisites = corequisites.next_sibling.text

            if exclusions:
                exclusions = exclusions.next_sibling.text

            course_data[course_code] = {"Title": course_title,
                                        "Description": description,
                                        "Exclusions": exclusions,
                                        "Prerequisites": prerequisites,
                                        "Corequisites": corequisites}

    with open('./data/utsc_courses.pickle', 'wb') as handle:
        pickle.dump(course_data, handle, protocol=pickle.HIGHEST_PROTOCOL)


def mine_utm_courses():
    """
    Mine UTM course data.
    :return: None
    """
    course_data = {}

    utm_api_url = "https://student.utm.utoronto.ca/timetable/timetable?yos=&subjectarea="

    for i in tqdm(range(1, utm_max_subjects + 1), desc="UTM"):
        request_url = utm_api_url + str(i) + "&session=" + session

        response = requests.get(request_url).text
        soup = BeautifulSoup(response, 'html5lib')
        results = soup.find_all("div", id=re.compile("-span$"))

        for result in results:
            course_title = result.find("h4").text.strip()

            info = re.search('(.*) - (.*)', course_title)
            course_code = info.group(1)

            if course_code in course_data:
                continue

            course_title = info.group(2)

            course_description = result.find("div", class_="alert alert-info infoCourseDetails infoCourse")

            key_terms = ["Exclusion:", "Prerequisite:", "Corequisite:"]

            for term in key_terms:
                index = str(course_description).find(term)
                if index > -1:
                    course_description = str(course_description)[:index]

            course_description = BeautifulSoup(str(course_description), 'html5lib').text.strip()

            exclusions = result.find("strong", text=re.compile("Exclusion:"))
            prerequisites = result.find("strong", text=re.compile("Prerequisites:"))
            corequisites = result.find("strong", text=re.compile("Corequisites:"))

            if exclusions:
                exclusions = str(exclusions.next_sibling).strip()

            if prerequisites:
                prerequisites = str(prerequisites.next_sibling).strip()

            if corequisites:
                corequisites = str(corequisites.next_sibling).strip()

            course_data[course_code] = {"Title": course_title,
                                        "Description": course_description,
                                        "Exclusions": exclusions,
                                        "Prerequisites": prerequisites,
                                        "Corequisites": corequisites}

    with open('./data/utm_courses.pickle', 'wb') as handle:
        pickle.dump(course_data, handle, protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == "__main__":
    if not os.path.exists("./data"):
        os.makedirs("./data")

    mine_utsg_courses()
    mine_utm_courses()
    mine_utsc_courses()