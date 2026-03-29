import unittest
from student import Student


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
