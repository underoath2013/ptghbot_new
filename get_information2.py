import openpyxl
book = openpyxl.open('ismen_nov.xlsx', read_only=True)
sheet = book.active

for row in range(1,sheet.max_row+1):
    A = sheet[row][0].value
    B = sheet[row][1].value
    C = sheet[row][2].value
    D = sheet[row][3].value
    E = sheet[row][4].value
    F = sheet[row][5].value
    G = sheet[row][6].value
        print(f'{A} {B} {C}  {D}  {E} {F} {G}')
