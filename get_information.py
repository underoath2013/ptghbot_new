import openpyxl
book = openpyxl.open('ismen_nov.xlsx', read_only=True)
sheet = book.active


def b_column():
    for row in range(1, sheet.max_row):
        a_column = sheet[row][0].value
        if a_column is None:
            a_column = ''
        c_column = sheet[row][2].value
        if c_column is None:
            c_column = ''
        b_column = sheet[row][1].value
        if b_column is None:
            continue
        else:
            print(' '.join(a_column.split()), ' '.join(b_column.split()), c_column)


b_column()


def f_column():
    for row in range(1, sheet.max_row):
        e_column = sheet[row][4].value
        if e_column is None:
            e_column = ''
        g_column = sheet[row][6].value
        if g_column is None:
            g_column = ''
        f_column = sheet[row][5].value
        if f_column is None:
            continue
        else:
            print(' '.join(e_column.split()), ' '.join(f_column.split()), g_column)


f_column()


