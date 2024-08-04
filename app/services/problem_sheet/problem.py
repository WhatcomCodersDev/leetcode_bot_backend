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
        }
    
    def get_category(self):
        return self.category
    
    def get_difficulty(self):
        return self.problem_difficulty
    
    def get_tag(self):
        return self.tag
    
    def get_id(self):
        return self.id
    
    def get_name(self):
        return self.name
    
    def get_link(self):
        return self.link
    
    def get_isInBlind75(self):
        return self.isInBlind75
    
    def get_isInBlind50(self):
        return self.isInBlind50
    
    def get_isInNeetcode(self):
        return self.isInNeetcode
    
    def get_isInGrind75(self):
        return self.isInGrind75
    
    def get_isInSeanPrasadList(self):
        return self.isInSeanPrasadList
    

