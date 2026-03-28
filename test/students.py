students = [{"name": "张三", "score": 90}, {"name": "李四", "score": 85}]


def add_stu(name, score):
    for stu in students:
        if stu["name"] == name:
            return False
    try:
        score_num = int(score)
        students.append({"name": name, "score": score_num})
        return True
    except ValueError:
        print("score must be number")
        return False


def del_stu(name):
    for stu in students:
        if stu["name"] == name:
            students.remove(stu)
            return True
    return False


def edit_stu(name, score):
    try:
        _score = int(score)
        for stu in students:
            if stu["name"] == name:
                stu["score"] = _score
                return True
    except ValueError:
        return False
    return False


def get_stu(name):
    for stu in students:
        if stu["name"] == name:
            return stu
    return None


def print_all():
    for stu in students:
        print(f"name: {stu['name']}, score: {stu['score']}")
