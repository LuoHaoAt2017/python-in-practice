class Student:
    def __init__(self):
        self.students = [{"name": "张三", "score": 90}, {"name": "李四", "score": 85}]

    def add_stu(self, name, score):
        for stu in self.students:
            if stu["name"] == name:
                return False
        try:
            score_num = int(score)
            self.students.append({"name": name, "score": score_num})
            return True
        except ValueError:
            print("score must be number")
            return False

    def del_stu(self, name):
        for stu in self.students:
            if stu["name"] == name:
                self.students.remove(stu)
                return True
        return False

    def edit_stu(self, name, score):
        try:
            _score = int(score)
            for stu in self.students:
                if stu["name"] == name:
                    stu["score"] = _score
                    return True
        except ValueError:
            return False
        return False

    def get_stu(self, name):
        for stu in self.students:
            if stu["name"] == name:
                return stu
        return None

    def print_all(self):
        for stu in self.students:
            print(f"name: {stu['name']}, score: {stu['score']}")
