

def parsing_changes_xlsx(sheet):
    """  Обрабатывает excel файл с изменениями к расписанию
    :param sheet: лист книги
    :type sheet: str
    """
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
    return schedule


def parsing_main_xlsx(sheet):
    """  Обрабатывает excel файл основного расписания
        :param sheet: лист книги
        :type sheet: str
    """
    main_schedule = []
    main_schedule_dict = {}
    j = -1
    k = 1
    for i in range(20):
        j = j + 3
        k = k + 3
        main_schedule.clear()
        for row in range(5, 30):
            column1 = sheet[row][j].value
            if column1 is None:
                continue
            column2 = sheet[row][k].value
            if column2 is None:
                column2 = ''
            result = str(column1) + ' ' + str(column2)
            main_schedule.append(result)
            main_schedule_dict[main_schedule[0]] = main_schedule[1:]

    j = 60
    k = 62
    for i in range(8):
        j = j + 3
        k = k + 3
        main_schedule.clear()
        for row in range(5, 30):
            column1 = sheet[row][j].value
            if column1 is None:
                continue
            column2 = sheet[row][k].value
            if column2 is None:
                column2 = ''
            result = str(column1) + ' ' + str(column2)
            main_schedule.append(result)
            main_schedule_dict[main_schedule[0]] = main_schedule[1:]
    return main_schedule_dict
