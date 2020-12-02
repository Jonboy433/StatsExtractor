import re
import os
import datetime
import calendar
import argparse

audit_totals = {}
months_in_input = set()


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
    total_ticket_count = 0
    print("reading from file {}".format(args.input_file))

    regex_request = re.compile('Request: (?P<RequestID>[0-9]{8})', re.IGNORECASE)
    regex_audit = re.compile(r'Property:(\s*)Audit Category(\s*)(?P<AuditCat>.*)', re.IGNORECASE)
    regex_status = re.compile(r'Status:(\s*)(?P<Status>.*?)(\s)(Active|Inactive)', re.IGNORECASE)
    regex_open = re.compile(r'Open Date:(\s*)(?P<OpenDate>.*?)(\s*)Close Date', re.IGNORECASE)
    regex_assignee = re.compile(r'Assignee:(\s*)(?P<Assignee>.*?)(\s*)SLA',re.IGNORECASE)
    regex_end = re.compile('ADP_15_Days_Event_for_Netcool.*', re.IGNORECASE)

    try:
        with open(args.input_file, "r", encoding='utf-8') as inputFile, open(get_detail_output_file_name(), 'w') as results:
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
                    # add to month set
                    add_month_to_set(int(date.group("OpenDate")[:2]))
                if cat:
                    results.write(cat.group("AuditCat"))
                    add_to_totals(cat.group("AuditCat"))
                if end:
                    total_ticket_count += 1
                    results.write('\n')
    except FileNotFoundError:
        print('Unable to find {} in the current directory'.format(args.input_file))

    print('Parsed {} tickets.\nGenerated output files {} and {}'.format(total_ticket_count, get_detail_output_file_name(), get_stats_output_file_name()))

    compile_stats(audit_totals.items())


def compile_stats(totals: dict) -> None:
    with open(get_stats_output_file_name(), 'w') as stats:
        stats.write('Category,Count\n')
        for key, value in sorted(totals):
            if key == '-':
                stats.write('N/A,' + str(value))
                print('N/A - ' + str(value))
            else:
                stats.write(key + ',' + str(value))
                print(key + ' - ' + str(value))
            stats.write('\n')


def add_month_to_set(month: int) -> None:
    months_in_input.add(month)


def get_month() -> str:
    # Take the month from the earliest ticket and use that for naming output file
    month_list = sorted(list(months_in_input))
    return calendar.month_name[month_list[0]][:3]


def get_detail_output_file_name() -> str:
    output_details_file = os.path.splitext(args.input_file)[0] + '_results_' + f"{datetime.datetime.now():%m}" \
                  + f"{datetime.datetime.now():%d}" + '.csv'

    return output_details_file


def get_stats_output_file_name() -> str:
    # For now it prints the month when you run it. Need to make it read month from input list
    output_stats_file = 'ServiceDeskStats_' + get_month() + str(datetime.datetime.now().year) + '.csv'

    return output_stats_file


def add_to_totals(cat: str) -> None:
    # check if cat already exists
    # if yes - increase current value by 1
    # if no - add to dict with a value of 1

    if cat in audit_totals.keys():
        audit_totals[cat] += 1
    else:
        audit_totals[cat] = 1


if __name__ == '__main__':
    main()
