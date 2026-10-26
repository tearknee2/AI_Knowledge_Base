# T1 冒烟测试：应用可导入、路由注册完整
# 对应任务书：docs/tutorial/14-实施路线图.md T1
from app.main import app

# 截至 T1，main.py 应有的全部业务路由（不含 FastAPI 自带的 /docs 等）
EXPECTED_ROUTES = {
    "/": {"GET"},
    "/users": {"POST"},
    "/knowledge-bases": {"POST", "GET"},
    "/knowledge-bases/{knowledge_base_id}": {"GET"},
    "/knowledge-bases/{knowledge_base_id}/documents": {"POST", "GET"},
}


def _route_map() -> dict[str, set[str]]:
    """从 app 实例提取 路径 -> 方法集合 的映射（剔除自动生成的 HEAD）。"""
    result: dict[str, set[str]] = {}
    for route in app.routes:
        if hasattr(route, "methods"):
            result.setdefault(route.path, set()).update(route.methods - {"HEAD"})
    return result


def test_app_importable_and_routes_registered():
    routes = _route_map()
    for path, expected_methods in EXPECTED_ROUTES.items():
        assert path in routes, f"缺少路由 {path}"
        missing = expected_methods - routes[path]
        assert not missing, f"路由 {path} 缺少方法 {missing}"
