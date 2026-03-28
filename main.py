students = [{"name": "张三", "score": 90}, {"name": "李四", "score": 85}]


def add_stu(name, score):
    for stu in students:
        if stu["name"] == name:
            return False
    students.append({"name": name, "score": score})
    return True


def del_stu(name):
    for stu in students:
        if stu["name"] == name:
            students.remove(stu)
            return True
    return False


def edit_stu(name, score):
    for stu in students:
        if stu["name"] == name:
            stu["score"] = score
            return True
    return False


def get_stu(name):
    for stu in students:
        if stu["name"] == name:
            return stu
    return None


def print_all():
    for stu in students:
        print(f"name: {stu['name']}, score: {stu['score']}")


add_stu("王五", 98)
print_all()
