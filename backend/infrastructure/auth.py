from fastapi import Header, HTTPException, Depends
from backend.domain.leave_entity import EmployeeModel

# Giả lập token authentication để lấy user hiện tại
def get_current_user(x_user_role: str = Header(default="Employee"), x_user_id: int = Header(default=1)):
    # Trong thực tế, bạn sẽ parse JWT token từ header 'Authorization'
    return {"id": x_user_id, "role": x_user_role}

def require_admin(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "Admin":
        raise HTTPException(status_code=403, detail="Chỉ Admin mới có quyền thực hiện chức năng này")
    return current_user
