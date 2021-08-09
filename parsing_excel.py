import openpyxl
sheet = book[context.user_data["dialog"]["sheet"]]
schedule = []
for row in range(1, sheet.max_row):
    a_column = sheet[row][0].value
    if a_column is None:
        a_column = ''
    c_column = sheet[row][2].value
    if c_column is None or c_column == 'ауд.':
        c_column = ''
    b_column = sheet[row][1].value
    if b_column is None:
        continue
    else:
        b_column_split = ' '.join(b_column.split())
        result_abc = str(a_column) + str(b_column_split) + str(c_column)
        schedule.append(result_abc)
for row in range(1, sheet.max_row):
    e_column = sheet[row][4].value
    if e_column is None:
        e_column = ''
    g_column = sheet[row][6].value
    if g_column is None or g_column == 'ауд.':
        g_column = ''
    f_column = sheet[row][5].value
    if f_column is None:
        continue
    else:
        f_column_split = ' '.join(f_column.split())
        result_efg = str(e_column) + str(f_column_split) + str(g_column)
        schedule.append(result_efg)