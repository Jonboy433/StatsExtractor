import re

audit_totals = {}

def main():
    print("reading from file ServiceDeskReport.txt..")

    regex_request = re.compile('Request: (?P<RequestID>[0-9]{8})', re.IGNORECASE)
    regex_audit = re.compile(r'Property:(\s*)Audit Category(\s*)(?P<AuditCat>.*)', re.IGNORECASE)
    regex_status = re.compile(r'Status:(\s*)(?P<Status>.*?)(\s)(Active|Inactive)', re.IGNORECASE)
    regex_open = re.compile(r'Open Date:(\s*)(?P<OpenDate>.*?)(\s*)Close Date', re.IGNORECASE)
    regex_assignee = re.compile(r'Assignee:(\s*)(?P<Assignee>.*?)(\s*)SLA',re.IGNORECASE)
    regex_end = re.compile('ADP_15_Days_Event_for_Netcool.*', re.IGNORECASE)

    with open("ServiceDeskReport.txt","r",encoding='utf-8') as inputFile, open('results.csv','w') as results:
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

    if inputFile.closed:
        print("Done")

    for key, value in sorted(audit_totals.items()):
        if key == '-':
            print('N/A - ' + str(value))
        else:
            print(key + ' - ' + str(value))

def add_to_totals(cat: str):
    #check if cat already exists
    #if yes - increase current value by 1
    #if no - add to dict with a value of 1

    if cat in audit_totals.keys():
        audit_totals[cat] += 1
    else:
        audit_totals[cat] = 1

if __name__ == '__main__':
    main()