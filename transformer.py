import json
import time
from datetime import datetime

# Example input JSON
input_json = {
  # (Input data as shown earlier)
}

# Helper function to convert RFC3339 string to Unix Epoch
def rfc3339_to_epoch(date_string):
    try:
        dt = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")
        return int(dt.timestamp())
    except ValueError:
        return None

# Transformation function
def transform_json(input_json):
    output = {}

    for key, value in input_json.items():
        if not key.strip():  # Omit empty keys
            continue
        
        key = key.strip()  # Sanitize key
        
        # Handle different data types based on the first key (S, N, BOOL, etc.)
        if 'S' in value:
            string_value = value['S'].strip()  # Sanitize value
            if not string_value:  # Omit empty strings
                continue
            # Check if the string is a date (RFC3339)
            epoch = rfc3339_to_epoch(string_value)
            if epoch:
                output[key] = epoch
            else:
                output[key] = string_value
        
        elif 'N' in value:
            try:
                number_value = value['N'].strip()
                number_value = number_value.lstrip('0') or '0'
                output[key] = float(number_value) if '.' in number_value else int(number_value)
            except ValueError:
                continue  # Omit invalid numeric values

        elif 'BOOL' in value:
            bool_value = value['BOOL'].strip().lower()
            if bool_value in ['1', 't', 'true']:
                output[key] = True
            elif bool_value in ['0', 'f', 'false']:
                output[key] = False
            else:
                continue  # Omit invalid boolean values

        elif 'NULL' in value:
            null_value = value['NULL'].strip().lower()
            if null_value in ['1', 't', 'true']:
                output[key] = None
            elif null_value in ['0', 'f', 'false']:
                continue  # Omit false null values
            else:
                continue  # Omit invalid null values
        
        elif 'L' in value:
            if not isinstance(value['L'], list):
                continue  # Omit invalid list
            list_output = []
            for item in value['L']:
                # Recursively handle each item in the list
                if 'S' in item and item['S'].strip():
                    list_output.append(item['S'].strip())
                elif 'N' in item:
                    try:
                        number_value = item['N'].strip().lstrip('0') or '0'
                        list_output.append(float(number_value) if '.' in number_value else int(number_value))
                    except ValueError:
                        continue
                elif 'BOOL' in item:
                    bool_value = item['BOOL'].strip().lower()
                    if bool_value in ['1', 't', 'true']:
                        list_output.append(True)
                    elif bool_value in ['0', 'f', 'false']:
                        list_output.append(False)
                # Skip nulls and unsupported types
            if list_output:
                output[key] = list_output

        elif 'M' in value:
            # Recursively transform nested maps
            map_output = transform_json(value['M'])
            if map_output:  # Omit empty maps
                output[key] = map_output

    return output

# Main function to handle input and output
def main(input_data):
    start_time = time.time()
    
    # Transform the input JSON
    transformed_data = transform_json(input_data)
    
    # Wrap the result in a list (as required by the output format)
    result = [transformed_data]
    
    # Print the output
    print(json.dumps(result, indent=2))
    
    # Print execution time
    execution_time = time.time() - start_time
    print(f"Processing time: {execution_time:.4f} seconds")

# Test the function with input data
main(input_json)
