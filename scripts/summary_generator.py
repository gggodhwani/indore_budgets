'Code for generating budget summary sheets'

import csv
import glob
import os
import simplejson

INPUT_FOLDER = "data/raw/"
OUT_FILE_CSV = "data/processed/csv/department_wise_summary.csv"
OUT_FILE_JSON = "data/processed/json/department_wise_summary.json"

class SummaryGenerator():
    def __init__(self):
        '''Initializes required variables'''
        self.data_map = {}
        self.year_list = []
        self.load_data_map()
        self.year_list.sort()

    def load_data_map(self):
        '''Loads data map from input files'''
        for input_file in glob.glob("%s*.csv" % INPUT_FOLDER):
            year = os.path.basename(input_file).split(".csv")[0]
            self.year_list.append(year)
            with open(input_file, 'rb') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                next(csv_reader, None)
                for row in csv_reader:
                    department_code = row[1].split(" ")[0]
                    department_name = row[1].split(department_code)[1].strip()
                    if not department_code in self.data_map:
                        self.data_map[department_code] = {"department_name" : department_name, "budget_head_map" : {}}
                    budget_head = row[2].split(" ")[0]
                    budget_head_description = row[2].split(budget_head)[1].strip()
                    if not budget_head in self.data_map[department_code]["budget_head_map"]:
                        self.data_map[department_code]["budget_head_map"][budget_head] = {"description" : budget_head_description, "values" : {}}
                    self.data_map[department_code]["budget_head_map"][budget_head]["values"][year] = float(row[3])

    def generate_summary_csv(self):
        '''Generates summary sheets'''
        summary_data = [["Department Code", "Department Name"] + self.year_list]
        for department_code in self.data_map:
            department_summary = [department_code]
            department_summary.append(self.data_map[department_code]["department_name"])
            for year in self.year_list:
                year_summary = 0
                for budget_head in self.data_map[department_code]["budget_head_map"]:
                    if year in self.data_map[department_code]["budget_head_map"][budget_head]["values"]:
                        year_summary += self.data_map[department_code]["budget_head_map"][budget_head]["values"][year]
                department_summary.append(year_summary)
            summary_data.append(department_summary)
        out_csv_file = open(OUT_FILE_CSV, "wb")
        csv_writer = csv.writer(out_csv_file, delimiter=',')
        for row in summary_data:
            csv_writer.writerow(row)
        out_csv_file.close()

    def generate_detailed_json(self):
        '''Generates detailed json'''
        summary_map = {"name":"budget", "children":[]}
        for key in self.data_map:
            department_map = {"name":self.data_map[key]["department_name"], "children":[]}
            for budget_head in self.data_map[key]["budget_head_map"]:
                budget_map = {"name":self.data_map[key]["budget_head_map"][budget_head]["description"]}
                budget_map.update(self.data_map[key]["budget_head_map"][budget_head]["values"])
                department_map["children"].append(budget_map)   
            summary_map["children"].append(department_map)
        output_json = simplejson.dumps(summary_map)
        output_file_obj = open(OUT_FILE_JSON, "wb")
        output_file_obj.write(output_json)
     
      
    def generate_summary_json(self):
        '''Generates summary json'''
        summary_map = {"name":"budget", "children":[]}
        for key in self.data_map:
            department_map = {"name":self.data_map[key]["department_name"]}
            for year in self.year_list:
                year_summary = 0
                for budget_head in self.data_map[key]["budget_head_map"]:
                    if year in self.data_map[key]["budget_head_map"][budget_head]["values"]:
                        year_summary += self.data_map[key]["budget_head_map"][budget_head]["values"][year]
                department_map[year] = year_summary
            summary_map["children"].append(department_map)
        output_json = simplejson.dumps(summary_map)
        output_file_obj = open(OUT_FILE_JSON, "wb")
        output_file_obj.write(output_json)
        
if __name__ == '__main__':
    obj = SummaryGenerator()
    obj.generate_summary_json()    
