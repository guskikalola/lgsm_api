from models import ServerDetailsModel
import re

def ServerDetailsParser(details: str):
    regex = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]|\t')
    by_lines = [regex.sub("",line) for line in details.split("\n") if line.find(":") != -1]
    
    details = {
        
    }
    
    for line in by_lines:
        row = line.split(":", maxsplit=2)
        
        key = row[0].strip()
        value = row[1].strip()

        details[key] = value

    return details