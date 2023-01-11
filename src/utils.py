import json
import ast

"""
    @Notice: This function will return the json in a file
    @Dev:   We open the file at the file path and return it as a json using json.load
"""
def get_dict_file(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

"""
    @Notice: This function will a string dict to dict
    @Dev:   We use the ast.literal_eval() to convert a string dict to dict object
"""
def convert_string_dict_to_dict(str_dict: str):
    return ast.literal_eval(str_dict)

"""
    @Notice: This function will build the file path regarding if it contains a "/" at the end
    @Dev:    We add a "/" between the two file path parts if it's missing
"""
def filepath_builder(filepath1, filepath2):
    if filepath1[-1] != "/":
        return filepath1 + '/' + filepath2
    return filepath1 + filepath2