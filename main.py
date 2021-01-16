import re
import os
import datetime
import calendar
import argparse
import xlsxwriter

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

    # create new xlsx file
    workbook = xlsxwriter.Workbook('test.xlsx')
    worksheet = workbook.add_worksheet('SD Details')

    regex_request = re.compile('Request: (?P<RequestID>[0-9]{8})', re.IGNORECASE)
    regex_audit = re.compile(r'Property:(\s*)Audit Category(\s*)(?P<AuditCat>.*)', re.IGNORECASE)
    regex_status = re.compile(r'Status:(\s*)(?P<Status>.*?)(\s)(Active|Inactive)', re.IGNORECASE)
    regex_open = re.compile(r'Open Date:(\s*)(?P<OpenDate>.*?)(\s*)Close Date', re.IGNORECASE)
    regex_assignee = re.compile(r'Assignee:(\s*)(?P<Assignee>.*?)(\s*)SLA', re.IGNORECASE)

    try:
        with open(args.input_file, "r", encoding='utf-8') as inputFile, open(get_detail_output_file_name(), 'w') as results:

            # start with row 0, col 0
            row = 0
            col = 0
            header = ['Ticket','Status','Assignee','Open Date','Audit Category']
            for item in header:
                worksheet.write(row, col, item)
                col += 1

            results.write('Ticket,Status,Assignee,Open Date,Audit Category\n')

            for line in inputFile:
                req = regex_request.match(line)
                cat = regex_audit.match(line)
                status = regex_status.match(line)
                date = regex_open.match(line)
                assignee = regex_assignee.match(line)

                if req:
                    row += 1
                    col = 0
                    results.write(req.group("RequestID") + ',')
                    add_to_worksheet(worksheet, row, col, req.group("RequestID"))
                    total_ticket_count += 1
                if status:
                    col = 1
                    results.write(status.group("Status") + ',')
                    add_to_worksheet(worksheet, row, col, status.group("Status"))
                if assignee:
                    col = 2
                    results.write("\"" + assignee.group("Assignee") + "\",")
                    add_to_worksheet(worksheet, row, col, assignee.group("Assignee"))
                if date:
                    col = 3
                    results.write(date.group("OpenDate") + ',')
                    add_to_worksheet(worksheet, row, col, date.group("OpenDate"))
                    # add to month set
                    add_month_to_set(int(date.group("OpenDate")[:2]))
                if cat:
                    col = 4
                    results.write(cat.group("AuditCat"))
                    add_to_worksheet(worksheet, row, col, cat.group("AuditCat"))
                    add_to_totals(cat.group("AuditCat"))
                    results.write('\n')

    except FileNotFoundError:
        print('Unable to find {} in the current directory'.format(args.input_file))

    print('Parsed {} tickets.\nGenerated output files {} and {}'.format(total_ticket_count, get_detail_output_file_name(), get_stats_output_file_name()))

    compile_stats(audit_totals.items())

    # close the xlsx file
    workbook.close()


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
    output_stats_file = 'ServiceDeskStats_' + get_month() + str(datetime.datetime.now().year) + '.csv'

    return output_stats_file


def get_xlsx_output_file_name() -> str:
    output_xlsx_file = 'ServiceDeskReport_' + get_month() + str(datetime.datetime.now().year) + '.xlsx'

    return output_xlsx_file


def add_to_totals(cat: str) -> None:
    # check if cat already exists
    # if yes - increase current value by 1
    # if no - add to dict with a value of 1

    if cat in audit_totals.keys():
        audit_totals[cat] += 1
    else:
        audit_totals[cat] = 1


def add_to_worksheet(sheet: xlsxwriter.worksheet.Worksheet, row: int, col: int, val: str) -> None:
    sheet.write(row, col, val)


if __name__ == '__main__':
    main()
