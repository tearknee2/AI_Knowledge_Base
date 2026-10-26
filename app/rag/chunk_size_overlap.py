# chunk_size_overlap
def split_text(text, chunk_size:int, chunk_overlap:int):
    if not isinstance(text,str):
        raise TypeError("Text must be of type str")
    if type(chunk_size) is not int:
        raise TypeError("Chunk size must be of type int")
    if type(chunk_overlap) is not int:
        raise TypeError("Chunk overlap must be of type int")

    result = []
    if chunk_size <= chunk_overlap or chunk_size <=0 or chunk_overlap <0:
        raise ValueError("给出的参数不合法")
    if not text:
        return result
    if chunk_size > len(text):
        return [text]

    for i in range(0, len(text), chunk_size-chunk_overlap):
        result.append(text[i:i+chunk_size])
    return result











