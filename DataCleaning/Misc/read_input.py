'''
Simple python subroutine to read in our specializedf input files
'''
def is_number(s):
    '''
    Check if str is a number. If so return as float
    PARAMETERS:
        s - string
    '''
    try:
        float(s)
        return True
    except ValueError:
        return False
def read_input_file(input_file):
    '''
    Read input file
    PARAMETERS:
        input_file - name of input file
    '''
    inputs = {}
    with open(input_file) as f:
        #Read file
        for line in f:
            if '=' in line: #Only read lines with '='
                inputs[line.split("=")[0].strip().lower()] = line.split("=")[1].strip()
            else: pass
        print("Successfully read in input file")
        for key,val in inputs.items():
            if is_number(val) == True and key != 'dir_list':
                inputs[key] = float(val)
            if key == 'dir_list':
                #Obtain individual obsids from list
                obsids = [inputs['dir_list'].split(',')[i].strip() for i in range(len(inputs['dir_list'].split(',')))]
                inputs['dir_list'] = obsids

    merge_bool = False

    return inputs,merge_bool

def read_password(input_file):
    '''
    read in password for database
    PARAMETERS:
        input_file - location of file with password
    '''
    pword = ''
    with open(input_file) as f:
        #Read file
        for line in f:
            if 'database_password' in line: #Only read lines with '='
                pword= line.split("=")[1].strip()
            else: pass
    return pword
