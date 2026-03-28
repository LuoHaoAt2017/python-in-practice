import unittest
import students


class TestStudentSystem(unittest.TestCase):

    def setUp(self):
        students.students = [
            {"name": "张三", "score": 90},
            {"name": "李四", "score": 85},
        ]

    # 每个 test_ 开头的方法就是一个测试用例
    def test_add_student(self):
        # 测试添加学生
        result = students.add_stu("王五", 100)
        self.assertEqual(result, True)  # 期望添加成功

    def test_add_duplicate_student(self):
        # 测试重复添加（应该失败）
        result = students.add_stu("张三", 60)
        self.assertEqual(result, False)

    def test_get_student(self):
        stu = students.get_stu("李四")
        self.assertIsNotNone(stu)  # 期望能找到

    def test_get_not_exist(self):
        stu = students.get_stu("不存在的人")
        self.assertIsNone(stu)  # 期望找不到

    def test_edit_score(self):
        students.edit_stu("张三", 99)
        stu = students.get_stu("张三")
        self.assertEqual(stu["score"], 99)

    def test_delete_student(self):
        result = students.del_stu("李四")
        self.assertEqual(result, True)


if __name__ == "__main__":
    unittest.main()
