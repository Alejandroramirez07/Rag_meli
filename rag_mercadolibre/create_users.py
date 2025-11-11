import hashlib
import os

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

admin_password = "admin"  
user_password = "user"    

print("Admin password hash:", hash_password(admin_password))
print("User password hash:", hash_password(user_password))