
def clean_text(text:str)->str:
    text = text.strip()
    lines = text.splitlines()
    text = [line.strip() for line in lines]
    result = []
    for line in text:
        if line == '' and result and result[-1] == '':
            continue
        result.append(line)
    return "\n".join(result)
#
# def clean_txt(text:str)->str:
#     text = text.strip()
#     lines = text.splitlines()
#     text = [line.strip() for line in lines]
#     result = []
#     previous_blank = False
#
#     for line in text:
#         if line == '':
#             pb = True
#         else:
#             pb = False
#
#         if previous_blank and pb:
#             continue
#         previous_blank = pb
#         result.append(line)
#
#     return "\n".join(result)
#
# def clean(text:str)->str:
#     text = text.strip()
#     lines = text.splitlines()
#     text = [line.strip() for line in lines]
#     result = []
#     previous_blank = False
#     for line in text:
#         if line == '':
#             is_blank = True
#         else:
#             is_blank = False
#         if is_blank and previous_blank:
#             continue
#         previous_blank = is_blank
#         result.append(line)
#     return "\n".join(result)
#
# print(clean_text(" hello  "))
# print(clean_text("hello\n\n\nworld"))
# print(clean_text(" hello\nworld"))
# print(clean_text(""))
#
# print(clean_text("hello\n   \nworld"))
# print("测试2",clean_text("\n\nhello\n\n"))
# print("测试3",repr(clean_text("   ")))
# repr() 是 Python 的内置函数，用于显示字符串的表示形式。
# 它能让 \n、空字符串等不容易看出来的内容更清楚。