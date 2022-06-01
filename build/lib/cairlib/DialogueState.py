import copy


class DialogueState:
    def __init__(self, d=None):
        self.dialogue_sentence = None
        self.addressed_speaker = None
        self.topic = None
        self.sentence_type = None
        self.pattern = None
        self.bool = None
        self.likelinesses = None
        self.flags = None
        self.addressed_community = None
        self.__dict__ = copy.deepcopy(d)

    def to_dict(self):
        dialogue_state_dict = copy.deepcopy(self.__dict__)
        return dialogue_state_dict
