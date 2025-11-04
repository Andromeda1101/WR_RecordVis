def load_word_list(filepath: str) -> list:
    with open(filepath, 'r', encoding='utf-8') as f:
        words = [line.strip() for line in f if line.strip()]
    return words

class RecordConfig:
    wordsfile: str = "words/3000words.txt"
    record_dir: str = "records"
    number_list = [str(i) for i in range(10)]
    alphabet_list_lower = [chr(i) for i in range(ord('a'), ord('z') + 1)]
    alphabet_list_upper = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
    body_parts = ["board", "palm", "thigh"]
    speeds = ["fast", "slow"]
    word_list = load_word_list(wordsfile)
    word_count: int = 100  # select words randomly from word_list
    # Redefined semantics:
    # - number_times: cycles of 0..9 per block (total items per block = 10 * number_times)
    # - alphabet_times: cycles of A..Z then a..z per block (total items per block = 52 * alphabet_times)
    # - word_times: number of words per block (total items per block = word_times)
    number_times: int = int(30 * 60 / 10)
    alphabet_times: int = int(15 * 60 / 52)
    word_times: int = int(15 * 60 / 4)


