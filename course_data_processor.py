import pickle
import csv
import re
import os

data = {}
processed_course_req = {}
id_count = 0
letter_num_dict = {"A": "1", "B": "2", "C": "3", "D": "4"}


def clean_up_course_code(course_code):
    """
    Returns the base of the given course code
    :param course_code: Course code
    :return: Base of the course code
    """
    if course_code[6].isdigit():
        code = course_code[:7].strip()
    else:
        code = course_code[:6].strip()

    return code


def add_course_to_global_data(course, campus_data, utsg=False, utm=False, utsc=False):
    """
    Adds the given course to the global data using the given campus data.
    :param course: Course code
    :param campus_data: Dictionary that would contain a dictionary of course information
    :param utsg: Boolean Flag
    :param utm: Boolean Flag
    :param utsc: Boolean Flag
    :return: None
    """
    global data
    global id_count

    if not utsg ^ utm ^ utsc:
        raise Exception("Adding new course to global data requires exactly one of the campus flags to be assigned True")

    code = clean_up_course_code(course)

    data[code] = {}
    data[code]["Label"] = code

    data[code]["Id"] = id_count
    id_count += 1

    data[code]["Title"] = campus_data[course]["Title"]

    if not campus_data[course]["Description"]:
        campus_data[course]["Description"] = ""

    if not campus_data[course]["Prerequisites"]:
        campus_data[course]["Prerequisites"] = ""

    if not campus_data[course]["Corequisites"]:
        campus_data[course]["Corequisites"] = ""

    if not campus_data[course]["Exclusions"]:
        campus_data[course]["Exclusions"] = ""

    if utsg:
        campus = "UTSG"
    elif utm:
        campus = "UTM"
    else:
        campus = "UTSC"

    data[code]["Description"] = campus_data[course]["Description"]

    if campus_data[course]["Prerequisites"]:
        data[code]["Prerequisites"] = "[{0}: {1}]".format(campus, campus_data[course]["Prerequisites"].strip())
    else:
        data[code]["Prerequisites"] = ""

    if campus_data[course]["Corequisites"]:
        data[code]["Corequisites"] = "[{0}: {1}]".format(campus, campus_data[course]["Corequisites"].strip())
    else:
        data[code]["Corequisites"] = ""

    if campus_data[course]["Exclusions"]:
        data[code]["Exclusions"] = "[{0}: {1}]".format(campus, campus_data[course]["Exclusions"].strip())
    else:
        data[code]["Exclusions"] = ""

    data[code]["Subject"] = data[code]["Label"][:3]
    data[code]["UTSG"] = "True" if utsg else "False"
    data[code]["UTM"] = "True" if utm else "False"
    data[code]["UTSC"] = "True" if utsc else "False"


def process_utsg_courses():
    """
    Process UTSG courses from ./data/utsg_courses.pickle
    :return: None
    """
    utsg_data = {}
    processed_courses = set()

    with open('./data/utsg_courses.pickle', 'rb') as file:
        try:
            utsg_data = pickle.load(file)
        except EOFError:
            print("Error")

    for course in utsg_data:
        code = clean_up_course_code(course)
        if code in processed_courses:
            continue
        add_course_to_global_data(course, utsg_data, utsg=True)
        processed_courses.add(code)


def process_utm_courses():
    """
    Process UTM courses from ./data/utm_courses.pickle, and appends data to any existing course in the global data.
    :return: None
    """
    utm_data = {}
    processed_courses = set()

    with open('./data/utm_courses.pickle', 'rb') as file:
        try:
            utm_data = pickle.load(file)
        except EOFError:
            print("Error")

    for course in utm_data:
        if course[6].isdigit():
            code = course[:7].strip()
        else:
            code = course[:6].strip()

        if code in processed_courses:
            continue

        if code in data:
            data[code]["UTM"] = "True"
            if utm_data[course]["Prerequisites"]:
                data[code]["Prerequisites"] += " [UTM: {0}]".format(utm_data[course]["Prerequisites"].strip())

            if utm_data[course]["Corequisites"]:
                data[code]["Corequisites"] += " [UTM: {0}]".format(utm_data[course]["Corequisites"].strip())

            if utm_data[course]["Exclusions"]:
                data[code]["Exclusions"] += " [UTM: {0}]".format(utm_data[course]["Exclusions"].strip())

            data[code]["Prerequisites"] = data[code]["Prerequisites"].lstrip()
            data[code]["Corequisites"] = data[code]["Corequisites"].lstrip()
            data[code]["Exclusions"] = data[code]["Exclusions"].lstrip()
        else:
            add_course_to_global_data(course, utm_data, utm=True)

        processed_courses.add(code)


def process_utsc_courses():
    """
    Process UTSC courses from ./data/utm_courses.pickle, and appends data to any existing course in the global data.
    :return:
    """
    global letter_num_dict
    utsc_data = {}
    processed_courses = set()

    with open('./data/utsc_courses.pickle', 'rb') as file:
        try:
            utsc_data = pickle.load(file)
        except EOFError:
            print("Error")

    for course in utsc_data:

        code = clean_up_course_code(course)

        if not isinstance(code[3], int) and len(code) == 6:
            code = code[:3] + letter_num_dict[code[3]] + code[4:]

        if code in processed_courses:
            continue

        if code in data:
            data[code]["UTSC"] = "True"

            if utsc_data[course]["Prerequisites"]:
                data[code]["Prerequisites"] += " [UTSC: {0}]".format(utsc_data[course]["Prerequisites"].strip())

            if utsc_data[course]["Corequisites"]:
                data[code]["Corequisites"] += " [UTSC: {0}]".format(utsc_data[course]["Corequisites"].strip())

            if utsc_data[course]["Exclusions"]:
                data[code]["Exclusions"] += " [UTSC: {0}]".format(utsc_data[course]["Exclusions"].strip())

            data[code]["Prerequisites"] = data[code]["Prerequisites"].lstrip()
            data[code]["Corequisites"] = data[code]["Corequisites"].lstrip()
            data[code]["Exclusions"] = data[code]["Exclusions"].lstrip()
        else:
            add_course_to_global_data(course, utsc_data, utsc=True)

        processed_courses.add(code)


def cleanup_data():
    """
    Go through the global course data, and extract cleaned up data (prerequisites, corequisites, exclusions) and store
    them in a global processed_course_req variable.
    :return: None
    """
    global id_count
    course_regex = "[A-Z]{3}[1-4A-D][0-9]{2}[0-9]?"

    code_only_courses = {}

    for course in data:
        prerequisites_match = re.findall(course_regex, data[course]["Prerequisites"])
        corequisites_match = re.findall(course_regex, data[course]["Corequisites"])
        exclusions_match = re.findall(course_regex, data[course]["Exclusions"])

        prereq_list = list(set(prerequisites_match))
        coreq_list = list(set(corequisites_match))
        exclusion_list = list(set(exclusions_match))

        for lst in [prereq_list, coreq_list, exclusion_list]:
            for lst_course in lst:

                alternate = None

                if not lst_course[3].isdigit():
                    alternate = lst_course[:3] + letter_num_dict[lst_course[3]] + lst_course[4:]

                if lst_course not in data and alternate not in data:
                    code_only_courses[lst_course] = {"Id": id_count, "Label": lst_course, "Description": "",
                                                     "Subject": lst_course[:3], "UTSG": "False", "UTM": "False",
                                                     "UTSC": "False", "Prerequisites": "", "Corequisites": "",
                                                     "Exclusions": ""}
                    id_count += 1

        processed_course_req[course] = {
            "Prerequisites Data": list(set(prerequisites_match)),
            "Corequisites Data": list(set(corequisites_match)),
            "Exclusions Data": list(set(exclusions_match))
        }

    for code_only_course in code_only_courses:
        data[code_only_course] = code_only_courses[code_only_course]


if __name__ == "__main__":
    process_utsg_courses()
    process_utm_courses()
    process_utsc_courses()

    cleanup_data()

    connections = set()

    if not os.path.exists("./csv"):
        os.makedirs("./csv")

    with open("./csv/nodes.csv", 'w') as csvfile:
        fieldnames = ["Id", "Label", "Title", "Description", "Subject", "UTSG", "UTM", "UTSC",
                      "Prerequisites", "Corequisites", "Exclusions"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data.values())

    with open("./csv/edges.csv", 'w') as csvfile:
        fieldnames = ["Source", "Target", "Type", "Weight"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        rows = []

        for course in data:
            if course not in processed_course_req:
                continue

            prereqs = processed_course_req[course]["Prerequisites Data"]

            for prereq in prereqs:
                selected_course = prereq

                if prereq:

                    if prereq not in data:
                        selected_course = prereq[:3] + letter_num_dict[prereq[3]] + prereq[4:]

                    if (data[selected_course]["Id"], data[course]["Id"]) in connections:
                        continue

                    rows.append({"Type": "Directed",
                                 "Weight": "1",
                                 "Source": data[selected_course]["Id"],
                                 "Target": data[course]["Id"]})

                    connections.add((data[selected_course]["Id"], data[course]["Id"]))

            coreqs = processed_course_req[course]["Corequisites Data"]

            for coreq in coreqs:
                selected_course = coreq

                if coreq:

                    if coreq not in data:
                        selected_course = coreq[:3] + letter_num_dict[coreq[3]] + coreq[4:]

                    if (data[selected_course]["Id"], data[course]["Id"]) in connections:
                        continue

                    rows.append({"Type": "Directed",
                                 "Weight": "1",
                                 "Source": data[selected_course]["Id"],
                                 "Target": data[course]["Id"]})

                    connections.add((data[selected_course]["Id"], data[course]["Id"]))

        writer.writerows(rows)