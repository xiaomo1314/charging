from models import User


def generate_uid():
    # 获取当前用户数
    count = User.query.count()
    new_number = count + 1
    return f"U{new_number:03d}"  # 补零，3位数字
