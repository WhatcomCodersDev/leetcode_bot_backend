from dataclasses import dataclass

@dataclass
class Problem:
    id: int
    name: str
    link: str
    category: str
    problem_difficulty: str
    tag: str
    isInBlind75: bool
    isInBlind50: bool
    isInNeetcode: bool
    isInGrind75: bool
    isInSeanPrasadList: bool
    # notes: str

    def __str__(self):
        return f"{self.id}. {self.name} (difficulty: {self.problem_difficulty}, tag: {self.tag}, category: {self.category})"

    def __repr__(self):
        return self.__str__()

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'link': self.link,
            'category': self.category,
            'problem_difficulty': self.problem_difficulty.lower(),
            'tag': self.tag,
            'isInBlind75': self.isInBlind75,
            'isInBlind50': self.isInBlind50,
            'isInNeetcode': self.isInNeetcode,
            'isInGrind75': self.isInGrind75,
            'isInSeanPrasadList': self.isInSeanPrasadList,
            # 'notes': self.notes
        }