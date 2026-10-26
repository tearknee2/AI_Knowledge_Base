from app.rag.chunk_size_overlap import split_text

"""---------------------"""
"""测试代码"""
r1 = split_text("ABCDEFGHIJKLMN",4,1)
print("1",r1)
r4 = split_text("ABCDEFGHIJKLMN",19,4)
print("4",r4)
r5 = split_text("",9,4)
print("5",r5)
try:
    r6 = split_text("ABCDEFGHIJKL",9,9)
    print("6",r6)
except ValueError as e:
    print("6",e)
try:
    r2 = split_text("ABCDEFGHIJKLMN",1,4)
    print("2",r2)
except ValueError as e:
    print("2",e)
try:
    r3 = split_text("ABCDEFGHIJKLMN",-4,1)
except ValueError as e:
    print("3",e)
try:
    r7 = split_text("ABCDEFGHIJKLMN",4,-1)
except ValueError as e:
    print("7",e)
try:
    r8 = split_text(None,4,1)
    print("8",r8)
except TypeError as e:
    print("8",e)
try:
    # 浮点数
    split_text("ABCDEFGHIJKLMN", 4.5, 1)
except TypeError as e:
    print("4.5",e)
try:
    # 字符串
    split_text("ABCDEFGHIJKLMN", "4", 1)
except TypeError as e:
    print("'4'",e)
try:
    # 布尔值
    split_text("ABCDEFGHIJKLMN", True, 0)
except TypeError as e:
    print("'True'",e)

# try:
print(split_text("ABCDEFGHIJKLMN", 2, 0))