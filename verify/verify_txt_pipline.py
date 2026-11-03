from pathlib import Path
from app.rag.txt_loader import load_txt
from app.rag.chunk_size_overlap import split_text

test_file = Path(__file__).parent / "sample.txt"
test_file.write_text(
    """
            短期：
        
        - 肚子咕咕叫、心慌、翻来覆去睡不着，睡眠变浅
        - 夜里容易醒，早上容易暴食
        
        长期：
        
        - 胃酸持续分泌，容易反酸、胃痛，伤胃黏膜
        - 代谢容易偏低，反而不利于减脂；肌肉更容易流失
        
        > 
        > 适合：晚饭吃得比较晚、下午吃得多，睡前一点不饿的情况，不用硬吃。
        > 不适合：明显饥饿、胃空得难受、低血糖人群。
        
        ### ✘ 吃饱睡觉（吃很饱立刻躺）
        
        这是更不推荐的：
        
        - 肠胃还在高强度消化，血液集中在胃肠道，大脑供氧变少，睡沉困难
        - 极易**胃食管反流、烧心、胀气**
        - 热量更容易囤积，长胖；夜间血脂负担更大
        - 多梦、睡不踏实
    """,
    encoding="utf-8",
)

text = load_txt(str(test_file))
result = split_text(text, 10,2)
print(result)

assert type(text) == str
assert type(result) == list
for item in result:
    assert len(item) <= 10
for i in range(len(result)-1):
    assert result[i][-2:] == result[i+1][:2]
assert text == text.strip()

test_file.unlink()