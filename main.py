import re
import os
import argparse

audit_totals = {}


def text_file(file_name):
    base, ext = os.path.splitext(file_name)
    if ext.lower() not in '.txt':
        raise argparse.ArgumentTypeError('File must have .txt extension')
    else:
        return file_name


parser = argparse.ArgumentParser(description='Extract SD stats from file')
parser.add_argument('input_file', type=text_file, help='The file to parse')
args = parser.parse_args()


def main():
    print("reading from file {}".format(args.input_file))

    regex_request = re.compile('Request: (?P<RequestID>[0-9]{8})', re.IGNORECASE)
    regex_audit = re.compile(r'Property:(\s*)Audit Category(\s*)(?P<AuditCat>.*)', re.IGNORECASE)
    regex_status = re.compile(r'Status:(\s*)(?P<Status>.*?)(\s)(Active|Inactive)', re.IGNORECASE)
    regex_open = re.compile(r'Open Date:(\s*)(?P<OpenDate>.*?)(\s*)Close Date', re.IGNORECASE)
    regex_assignee = re.compile(r'Assignee:(\s*)(?P<Assignee>.*?)(\s*)SLA',re.IGNORECASE)
    regex_end = re.compile('ADP_15_Days_Event_for_Netcool.*', re.IGNORECASE)

    try:
        with open(args.input_file, "r", encoding='utf-8') as inputFile, open('results.csv', 'w') as results:
            results.write('Ticket,Status,Assignee,Open Date,Audit Category\n')
            for line in inputFile:
                req = regex_request.match(line)
                cat = regex_audit.match(line)
                status = regex_status.match(line)
                date = regex_open.match(line)
                assignee = regex_assignee.match(line)
                end = regex_end.match(line)

                if req:
                    results.write(req.group("RequestID") + ',')
                if status:
                    results.write(status.group("Status") + ',')
                if assignee:
                    results.write("\"" + assignee.group("Assignee") + "\",")
                if date:
                    results.write(date.group("OpenDate") + ',')
                if cat:
                    results.write(cat.group("AuditCat"))
                    add_to_totals(cat.group("AuditCat"))
                if end:
                    results.write('\n')
    except FileNotFoundError:
        print('Unable to find {} in the current directory'.format(args.input_file))

    for key, value in sorted(audit_totals.items()):
        if key == '-':
            print('N/A - ' + str(value))
        else:
            print(key + ' - ' + str(value))

def add_to_totals(cat: str):
    # check if cat already exists
    # if yes - increase current value by 1
    # if no - add to dict with a value of 1

    if cat in audit_totals.keys():
        audit_totals[cat] += 1
    else:
        audit_totals[cat] = 1


if __name__ == '__main__':
    main()
