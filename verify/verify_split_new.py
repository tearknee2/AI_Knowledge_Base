import unittest


# 假设你的源文件名为 text_splitter.py
# from text_splitter import split_long_paragraph
# 这里直接把函数放进来为了演示自包含运行
def split_long_paragraph(text: str, chunk_size=500, chunk_overlap=50):
    """拆分过长的单个段落"""
    if not isinstance(text, str):
        raise TypeError("Text must be of type str")
    if type(chunk_size) is not int:
        raise TypeError("Chunk size must be of type int")
    if type(chunk_overlap) is not int:
        raise TypeError("Chunk overlap must be of type int")
    result = []
    if chunk_size <= chunk_overlap or chunk_size <= 0 or chunk_overlap < 0:
        raise ValueError("给出的参数不合法")
    if not text:
        return result
    if len(text) <= chunk_size:
        return [text] if text else []
    for start in range(0, len(text), chunk_size - chunk_overlap):
        result.append(text[start:start + chunk_size])
        if start + chunk_size >= len(text):
            break
    return result


class TestSplitLongParagraph(unittest.TestCase):

    def _generate_test_string(self, length):
        """生成用于测试的字符串，保证字符唯一性以便验证重叠部分"""
        # 使用循环的字母表，保证每个位置的字符不仅可读，而且能通过内容比对重叠
        base_str = "abcdefghijklmnopqrstuvwxyz"
        return "".join([base_str[i % 26] for i in range(length)])

    def test_length_0(self):
        text = self._generate_test_string(0)
        result = split_long_paragraph(text)
        self.assertEqual(len(result), 0)
        self.assertEqual(result, [])

    def test_length_100(self):
        text = self._generate_test_string(100)
        result = split_long_paragraph(text)
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[0]), 100)
        self.assertEqual(result[0], text)

    def test_length_500(self):
        text = self._generate_test_string(500)
        result = split_long_paragraph(text)
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[0]), 500)
        self.assertEqual(result[0], text)

    def test_length_501(self):
        text = self._generate_test_string(501)
        result = split_long_paragraph(text)

        # 验证数量和长度
        self.assertEqual(len(result), 2)
        self.assertEqual(len(result[0]), 500)
        self.assertEqual(len(result[1]), 51)

        # 验证重叠内容：前一块的最后 50 个字符，应该等于后一块的前 50 个字符
        overlap_prev = result[0][-50:]
        overlap_next = result[1][:50]
        self.assertEqual(overlap_prev, overlap_next, "501 长度时重叠内容不匹配")

    def test_length_800(self):
        text = self._generate_test_string(800)
        result = split_long_paragraph(text)

        self.assertEqual(len(result), 2)
        self.assertEqual(len(result[0]), 500)
        self.assertEqual(len(result[1]), 350)

        overlap_prev = result[0][-50:]
        overlap_next = result[1][:50]
        self.assertEqual(overlap_prev, overlap_next, "800 长度时重叠内容不匹配")

    def test_length_1400(self):
        text = self._generate_test_string(1400)
        result = split_long_paragraph(text)

        # 验证数量和长度
        self.assertEqual(len(result), 3)
        self.assertEqual(len(result[0]), 500)
        self.assertEqual(len(result[1]), 500)
        self.assertEqual(len(result[2]), 500)
        # 验证第一块和第二块的重叠
        self.assertEqual(result[0][-50:], result[1][:50], "1400 长度：Chunk 0 和 Chunk 1 重叠不匹配")
        # 验证第二块和第三块的重叠
        self.assertEqual(result[1][-50:], result[2][:50], "1400 长度：Chunk 1 和 Chunk 2 重叠不匹配")

        # 额外验证：确保这三个 Chunk 拼接后能完美还原完整原文（去掉重叠部分）
        # Chunk 0 + Chunk 1的截断部分 + Chunk 2的截断部分
        reconstructed_text = result[0] + result[1][50:] + result[2][50:]
        self.assertEqual(reconstructed_text, text, "拼接后的文本与原文不匹配")

    def test_invalid_parameters(self):
        """测试非法参数（防呆设计）"""
        with self.assertRaises(ValueError):
            # chunk_size <= chunk_overlap
            split_long_paragraph("test", chunk_size=50, chunk_overlap=50)
        with self.assertRaises(ValueError):
            # chunk_size <= 0
            split_long_paragraph("test", chunk_size=0, chunk_overlap=10)
        with self.assertRaises(ValueError):
            # chunk_overlap < 0
            split_long_paragraph("test", chunk_size=100, chunk_overlap=-1)
        with self.assertRaises(TypeError):
            # 非字符串输入
            split_long_paragraph(12345)


if __name__ == '__main__':
    # 运行测试，verbosity=2 会输出每一个测试用例的详细结果
    unittest.main(verbosity=2)