from pathlib import Path
from app.rag.txt_loader import load_txt

test_file = Path(__file__).parent / "sample.txt"
test_file.write_text(
    "Python是一种编程语言。\nPython支持多种编程范式",
    encoding="utf-8"
)

text = load_txt(str(test_file))

print("读取结果：")
print(text)
print("返回类型：", type(text))



fake_path = Path(__file__).parent / "sample1.txt"
try:
    text1 = load_txt(str(fake_path))
    print("读取结果：")
    print(text1)
except FileNotFoundError as e:
    print("文件不存在",e)

fake_path2 = Path(__file__).parent / "sample2.docx"
fake_path2.write_text(
    "Python是一种编程语言。\nPython支持多种编程范式",
    encoding="utf-8"
)
try:
    text2 = load_txt(str(fake_path2))
    print("读取结果：")
    print(text2)
except ValueError as e:
    print("扩展名错误",e)

fake_path3 = Path(__file__).parent / "sample3.txt"
fake_path3.write_text("", encoding="utf-8")

text3 = load_txt(str(fake_path3))
print(text3, [text3],type(text3))

test_file.unlink()
fake_path2.unlink()
fake_path3.unlink()