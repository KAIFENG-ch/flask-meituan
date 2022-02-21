import bcrypt

password = '123456'.encode()
hashed = bcrypt.hashpw(password, bcrypt.gensalt())
print(type(hashed))
print(hashed)
if bcrypt.checkpw(password, hashed):
    print("yes")
