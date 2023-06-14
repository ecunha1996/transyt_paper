import xlwt
import os

def crawl_result_directories(dir):

    all_paths = [f.path for f in os.scandir(dir) if f.is_dir()]

    dic_growth = {}
    dic_no_growth = {}

    for path in all_paths:
        path_split = path.split("/")

        identifier = int(path_split[len(path_split)-1])

        path = path + "/results"

        if os.path.exists(path): #check if this is a results directory
            dic_growth[identifier] = read_result_file(path + "/biolog_compounds.txt")
            dic_no_growth[identifier] = read_result_file(path + "/biolog_compounds_no_growth.txt")
        else:
            dic_growth[identifier] = None
            dic_no_growth[identifier] = None



    return dic_growth, dic_no_growth

def read_result_file(path):
    dic = {}

    try:
        for line in open(path, "r"):

            aux = line.split("\t")
            dic[aux[0]] = aux[1]
    except:
        return None

    return dic


def save_excel_format(dic, dic_no_growth, path):

    book = xlwt.Workbook()
    sheet = book.add_sheet("growth")
    sheet2 = book.add_sheet("no_growth")

    sheet.write(0, 0, "compound")
    sheet2.write(0, 0, "compound")

    positions = {}
    col = 1

    all_compounds = []

    for key in dic.keys():
        if dic[key] is not None:
            for cpd in dic[key].keys():
                if cpd not in all_compounds:
                    all_compounds.append(cpd)

    all_compounds = sorted(all_compounds)

    for i in range(0, len(all_compounds)):
        current_row = i+1
        sheet.write(current_row, 0, all_compounds[i])
        sheet2.write(current_row, 0, all_compounds[i])
        positions[all_compounds[i]] = current_row

    for key in sorted(dic.keys()):
        sheet.write(0, col, key)
        sub_res = dic[key]

        for cpd in all_compounds:

            text = "No_Growth"

            if sub_res is None:
                text = "No_Results"
            elif sub_res is not None and cpd in sub_res:
                text = sub_res[cpd]

            sheet.write(positions[cpd], col, text.strip())

        col += 1

    col = 1

    for key in sorted(dic_no_growth.keys()):
        sheet2.write(0, col, key)
        sub_res = dic_no_growth[key]

        for cpd in all_compounds:

            text = "Growth"

            if sub_res is None:
                text = "No_Results"
            elif sub_res is not None and cpd in sub_res:
                text = sub_res[cpd]

            sheet2.write(positions[cpd], col, text.strip())

        col += 1

    book.save(path)


if __name__ == '__main__':
    main_path = "/biolog/patric_results"
    dirs = [f.path for f in os.scandir(main_path) if f.is_dir()]

    for dir in dirs:
        res_growth, res_no_growth = crawl_result_directories(dir)
        save_excel_format(res_growth, res_no_growth, dir + "_results.xls")
