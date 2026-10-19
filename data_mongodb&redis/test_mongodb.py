from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")

db = client["QL_TuyenDung"]

print("Ket noi MongoDB thanh cong")
print("So viec lam:", db["QL_ViecLam"].count_documents({}))