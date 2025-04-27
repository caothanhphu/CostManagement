# Xóa thư mục __pycache__ (Force để xóa không cần hỏi, Recurse để xóa đệ quy)
Get-ChildItem -Path . -Include __pycache__ -Recurse -Force | Remove-Item -Recurse -Force

# Xóa file .pyc, .pyo
Get-ChildItem -Path . -Include *.pyc, *.pyo -Recurse -Force | Remove-Item -Force