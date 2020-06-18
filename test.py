# def read_css(file_name):
#     css = ""
#     with open("./"+file_name,mode="r")as file:
#         css = file.read()
#     return str(css)

# print(read_css("test.css"))

with open("./test.css",mode="r")as file:
        print(file.read())