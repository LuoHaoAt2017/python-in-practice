import unittest
from tests.model.student import Student

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


class TestStudent(unittest.TestCase):

    def setUp(self):
        self.student = Student()

    # 每个 test_ 开头的方法就是一个测试用例
    def test_add_student(self):
        # 测试添加学生
        result = self.student.add_stu("王五", 100)
        self.assertEqual(result, True)  # 期望添加成功

    def test_add_duplicate_student(self):
        # 测试重复添加（应该失败）
        result = self.student.add_stu("张三", 60)
        self.assertEqual(result, False)

    def test_get_student(self):
        stu = self.student.get_stu("李四")
        self.assertIsNotNone(stu)  # 期望能找到

    def test_get_not_exist(self):
        stu = self.student.get_stu("不存在的人")
        self.assertIsNone(stu)  # 期望找不到

    def test_edit_score(self):
        self.student.edit_stu("张三", 99)
        stu = self.student.get_stu("张三")
        self.assertEqual(stu["score"], 99)

    def test_delete_student(self):
        result = self.student.del_stu("李四")
        self.assertEqual(result, True)


if __name__ == "__main__":
    unittest.main()
