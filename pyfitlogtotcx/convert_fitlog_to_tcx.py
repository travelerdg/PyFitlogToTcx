##############################################################################
# MIT License
#
# Copyright (c) 2024 Brad D. Parker
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
##############################################################################

##############################################################################
# This program will convert a SportTracks FITLOG file either into a single 
# Garmin TCX file or multiple TCX files, one per activity. 
#
# Author: Brad D. Parker
# Contact: bdparker@gmail.com
##############################################################################

import os
import sys
import argparse
from datetime import datetime, timedelta
from lxml import etree as ET
import csv

valid_sports = ["Running", "Biking", "Multisport", "Other"]

def get_sport_mapping(sport_mapping_file):
    print(f"Parsing {sport_mapping_file}")
    sport_dictionary = {}
    with open(sport_mapping_file, mode='r', encoding="utf-8") as infile: # for special characters in mapped sports
        reader = csv.reader(infile, skipinitialspace=True, quoting=csv.QUOTE_STRINGS)
        sport_dictionary = {rows[0]:rows[1] for rows in reader}
    return sport_dictionary

def find_unsupported_activities(fitlog_filename, sport_mapping):
    invalid_sports = []
    fitlog_tree = ET.parse(fitlog_filename)
    fitlog_root = fitlog_tree.getroot()
    for activity in fitlog_root.findall(".//Activity", fitlog_root.nsmap):
        category = activity.find("Category", fitlog_root.nsmap)
        sport_name=category.get("Name")
        if (sport_name not in valid_sports and sport_name not in invalid_sports):
            invalid_sports.append(sport_name)
    unmapped_sports = []
    for sport in invalid_sports:
        if sport in sport_mapping:
            print(f"{sport} will be saved as {sport_mapping[sport]}")
        else:
            unmapped_sports.append(sport)
    
    return unmapped_sports
        
def convert_fitlog_to_tcx(fitlog_filename, output_folder, sport_mapping, split):

    fitlog_tree = ET.parse(fitlog_filename)
    fitlog_root = fitlog_tree.getroot()

    print(f"Starting")
    # TCX Scheam
    schemaLocation_type = ET.QName("http://www.w3.org/2001/XMLSchema-instance", "schemaLocation")
    # TCX Namespaces
    tcx_nslist = {
    'ns5':'http://www.garmin.com/xmlschemas/ActivityGoals/v1',
    'ns3':'http://www.garmin.com/xmlschemas/ActivityExtension/v2',
    'ns2':'http://www.garmin.com/xmlschemas/UserProfile/v2', 
    'ns4':'http://www.garmin.com/xmlschemas/ProfileExtension/v1', 
    'xsi':'http://www.w3.org/2001/XMLSchema-instance', 
    None: 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'}
    if not os.path.exists(output_folder):
        # If directory doesn't exist, create it
        os.makedirs(output_folder)

    if (split):
        for activity in fitlog_root.findall(".//Activity", fitlog_root.nsmap):
            tcx_root = ET.Element("TrainingCenterDatabase", 
                                {schemaLocation_type: "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd"}, 
                                nsmap=tcx_nslist)
            tcx_activities = ET.SubElement(tcx_root, "Activities")
            # Add author
            add_author(tcx_root)
            
            start_time = write_activity(fitlog_root, activity, tcx_activities, sport_mapping)

            tcx_tree = ET.ElementTree(tcx_root)
            tcx_filename = f"{output_folder}/{start_time.strftime('%Y%m%dT%H%M%SZ')}.tcx"
            tcx_tree.write(tcx_filename, xml_declaration=True, encoding='UTF-8', pretty_print=True)
            print(f"Activity converted. TCX file saved at {tcx_filename}")
    else:     #if (not split):
        tcx_root = ET.Element("TrainingCenterDatabase", 
                    {schemaLocation_type: "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd"}, 
                    nsmap=tcx_nslist)
        tcx_activities = ET.SubElement(tcx_root, "Activities")
        for activity in fitlog_root.findall(".//Activity", fitlog_root.nsmap):
            write_activity(fitlog_root, activity, tcx_activities, sport_mapping)

        # Add author
        add_author(tcx_root)
        tcx_tree = ET.ElementTree(tcx_root)

        # Get just the root name of the input file path
        fitlog_root_name = os.path.basename(fitlog_filename).split('.')[0]

        tcx_filename = f"{output_folder}/{fitlog_root_name}-converted-{datetime.now().strftime('%Y%m%dT%H%M%SZ')}.tcx"
        tcx_tree.write(tcx_filename, xml_declaration=True, encoding='UTF-8', pretty_print=True)
        print(f"All activities converted. TCX file saved at {tcx_filename}")

# Add the author block
def add_author(tcx_root):    
    xsi_type = ET.QName("http://www.w3.org/2001/XMLSchema-instance", "type")
    author = ET.SubElement(tcx_root, "Author", {xsi_type: "Application_t"})
    ET.SubElement(author, "Name").text = "PyFitlogToTcx"
    author_build = ET.SubElement(author, "Build")
    author_version = ET.SubElement(author_build, "Version")
    ET.SubElement(author_version, "VersionMajor").text = "1"
    ET.SubElement(author_version, "VersionMinor").text = "0"
    ET.SubElement(author_version, "BuildMajor").text = "1"
    ET.SubElement(author_version, "BuildMinor").text = "0"

# Write a single activity to the tcx_activities element
def write_activity(fitlog_root, activity, tcx_activities, sport_mapping):
    # Get SportTracks Activity Information
    metadata = activity.find("Metadata", fitlog_root.nsmap)
    duration = activity.find("Duration", fitlog_root.nsmap)
    distance = activity.find("Distance", fitlog_root.nsmap)
    calories = activity.find("Calories", fitlog_root.nsmap)
    category = activity.find("Category", fitlog_root.nsmap)
    sport_name=category.get("Name")
    if sport_name in  sport_mapping:
        sport_name = sport_mapping[sport_name]
    location = activity.find("Location", fitlog_root.nsmap)
    start_time_str = activity.get("StartTime")
    start_time = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M:%SZ")

    print(f"Converting activity starting at {start_time}...")
    tcx_activity = ET.SubElement(tcx_activities, "Activity", Sport=sport_name)
    tcx_id = ET.SubElement(tcx_activity, "Id").text=activity.get("Id")
    if metadata is not None:
        xsi_type = ET.QName("http://www.w3.org/2001/XMLSchema-instance", "type")
        creator = ET.SubElement(tcx_activity, "Creator", {xsi_type: "Device_t"})
        name = ET.SubElement(creator, "Name")
        name.text = metadata.get("Source")

    if duration is not None:
       ET.SubElement(tcx_activity, "TotalTimeSeconds").text=duration.get("TotalSeconds")
    if distance is not None:
       ET.SubElement(tcx_activity, "DistanceMeters").text=distance.get("TotalMeters")
    if calories is not None:
        ET.SubElement(tcx_activity, "Calories").text=calories.get("TotalCal")
    if activity.find("Laps", fitlog_root.nsmap) is not None:
        laps=activity.find("Laps", fitlog_root.nsmap).findall("Lap", fitlog_root.nsmap)
        number_of_laps=len(laps)
        lap_number=0
        for lap in laps:
            lap_start_time_str = lap.get("StartTime")
            lap_start_time = datetime.strptime(lap_start_time_str, "%Y-%m-%dT%H:%M:%SZ")
            lap_duration = lap.get("DurationSeconds")
            lap_caloriesElem = lap.find("Calories", fitlog_root.nsmap)
            next_lap_start_time = 0
            if lap_number+1 < number_of_laps:
                next_lap_start_str = laps[lap_number+1].get("StartTime")
                next_lap_start_time = datetime.strptime(next_lap_start_str, "%Y-%m-%dT%H:%M:%SZ")

            tcx_lap = ET.SubElement(tcx_activity, "Lap", StartTime=lap_start_time.strftime("%Y-%m-%dT%H:%M:%SZ"))
            ET.SubElement(tcx_lap, "TotalTimeSeconds").text=lap_duration

            if lap_caloriesElem is not None:
                ET.SubElement(tcx_lap, "Calories").text=lap_caloriesElem.get("TotalCal")
            tcx_track = ET.SubElement(tcx_lap, "Track")
            for point in activity.findall(".//pt", fitlog_root.nsmap):
                timeoffset = int(point.get("tm"))
                point_time=(start_time + timedelta(seconds=timeoffset))
                if (point_time >= lap_start_time) and ((next_lap_start_time == 0) or (point_time < next_lap_start_time)):
                    trackpoint = ET.SubElement(tcx_track, "Trackpoint")
                    ET.SubElement(trackpoint, "Time").text = point_time.strftime("%Y-%m-%dT%H:%M:%SZ")
                    latitude=point.get("lat")
                    longitude=point.get("lon")
                    # Don't record point if no lat/lon
                    if (latitude is not None and longitude is not None):
                        tk_position = ET.SubElement(trackpoint, "Position")#.extend([ET.Element("LatitudeDegrees"), ET.Element("LongitudeDegrees")])
                        ET.SubElement(tk_position, "LatitudeDegrees").text =latitude 
                        ET.SubElement(tk_position, "LongitudeDegrees").text = longitude
                    #Only record Alt if it is available
                    altitude=point.get("ele")
                    if (altitude is not None):
                        ET.SubElement(trackpoint, "AltitudeMeters").text = altitude
                    heartrate=point.get("hr")
                    if (heartrate is not None):
                        hrbpm = ET.SubElement(tcx_activity, "HeartRateBpm", {xsi_type: "HeartRateInBeatsPerMinute_t"})
                        ET.SubElement(hrbpm, "Value").text=heartrate
            lap_number = lap_number + 1
    return start_time

# Main application entry point
def entry_point():
    import pkg_resources  # part of setuptools

    # Create argument parser
    parser = argparse.ArgumentParser(description='Converts a SportTracks fitlog file into Garmin TCX files')

    # Add arguments
    parser.add_argument('--input', type=str, required=True, help='Input fitlog file')
    parser.add_argument('--output', type=str, required=True, help='Output directory')
    parser.add_argument('--mapping', type=str, required=False, help='Sport name mapping file')
    parser.add_argument('--split', action='store_true', help='Split the input file into multiple TCX files - one per activity')


    # Parse the arguments
    args = parser.parse_args()
    
    sport_mapping = []
    if args.mapping is not None:
        sport_mapping = get_sport_mapping(args.mapping)
        print(f"Found {len(sport_mapping)} sets of replacement strings.")

    invalid_sports = find_unsupported_activities(args.input, sport_mapping)

    if len(invalid_sports) > 0:
        print(f"The input file contains unsupported activity types. These can be replaced by providing a mapping file with the --mapping option.")
        print(f"The format of the file is standard CSV. Each line should have the activity type to replace followed by the replacement value.")
        print(f"Supported sports are: {valid_sports}")
        print(f"Unsupported sports found in the input file: {invalid_sports}")
        # for sport in invalid_sports:
        #     print(f"No match for {sport}")
        exit
    else:
        # Print the names in the desired order
        print(f"Reading FITLOG from {args.input} and saving as TCX at {args.output}")
        fitlog_filename = args.input
        output_folder = args.output
        convert_fitlog_to_tcx(fitlog_filename, output_folder, sport_mapping, args.split)


# Main application entry point
if __name__ == '__main__':
    entry_point()
