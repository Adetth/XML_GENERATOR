import xml_analyzer as XA
#TESTING CODE
shared_var = XA.XMLAnalyzer()

shared_var.load_file(r"C:\Users\Adetth\Documents\Projects\XMLGenerator\MPB_1.2 Manage New Hires.xml")

x = shared_var.get_rowcols()

# for row in x["rows"]:
#     if row["type"] == "MEMBER":
#         print(row)

for a in x:
    for b in x[a]:
        print(a,b)