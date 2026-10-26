from pathlib import Path
from app.rag.text_cleaner import clean_text

def load_txt(file_path: str) ->str:
    """
    :param file_path:上传文件的实际保存路径
    :return: 文件正文字符串
    """
    # 1.将字符串路径转换成Path对象
    p = Path(file_path)

    # 2.检查文件是否存在，文件扩展名是否为.txt
    if not p.is_file():
        raise FileNotFoundError("文件不存在或路径不是文件")
    if p.suffix != '.txt':
        raise ValueError("文件类型有误")

    # 3.读取文件正文并返回
    text = p.read_text(encoding="utf-8")
    return clean_text(text)
