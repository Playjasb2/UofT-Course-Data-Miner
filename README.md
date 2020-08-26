# UofT Course Data Miner

This is the tool to mine course data from University of Toronto, and process them as csv files, ready to be imported into Gephi. 

The scripts works as of August 2020.

There are currently two main scripts at work here:

- `course_data_miner.py`: mines the UofT course data from all three campuses, and store them as .pickle files in the data folder.
- `course_data_processor.py`: processes the .pickle files from the previous script, and output two files in the csv folder: nodes.csv and edges.csv.
  
The nodes.csv file contains data on all the courses, while edges.csv contains all the connections between the courses. Both of these files are in a format that would be ready to be imported in a program called Gephi.

[Gephi](https://gephi.org) is a program that allows us to simulate network graphs, and it can produce reports and perform analysis on the graph's topology.

I actually used this program to export the graph as a [static webpage](https://uoft-course-graph.herokuapp.com), using the Sigma js plugin.

As with any data mining tools, it's possible for the scripts to break if University of Toronto decides to drastically change the way they deliver course information. 

If the scripts do break, this README will be updated to reflect the status. As of right now, the scripts do need to be refactored so it's better structured.

The scripts do require the following installed in your environment:

- Python 3 or later
- bs4
- requests
- tqdm