from time import perf_counter

class Log:
    def __init__(self, filepath):
        self.filepath = filepath
        self.body_part: str = ""
        self.content: str = ""
        self.speed: str = ""
        self.start = perf_counter()
        self.end = perf_counter()
        # new optional fields
        self.trial_index: int | None = None
        self.stimulus: str = ""

    def set_experiment_info(self, body_part: str, content: str, speed: str, trial_index: int | None = None, stimulus: str = ""):
        self.body_part = body_part
        self.content = content
        self.speed = speed
        # set optional fields if provided
        self.trial_index = trial_index
        self.stimulus = stimulus

    def record_start(self):
        self.start = perf_counter()
    
    def record_end(self):
        self.end = perf_counter()

    def save_log(self):
        log = {}
        log['body_part'] = self.body_part
        # record category ("number"/"alphabet"/"word")
        log['category'] = self.content
        # record concrete content, e.g., "1", "A", "apple"
        log['content'] = self.stimulus
        log['speed'] = self.speed
        log['trial_index'] = self.trial_index
        log['start'] = self.start
        log['end'] = self.end

        with open(self.filepath, 'a', encoding='utf-8') as f:
            f.write(str(log) + '\n')
