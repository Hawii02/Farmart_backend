from flask_bcrypt import Bcrypt

from flask_bcrypt import Bcrypt

# Initialize Bcrypt
bcrypt = Bcrypt()

# Test password
password = "password123"
hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

print(f"Original: {password}")
print(f"Hashed: {hashed_password}")

# Verify password
if bcrypt.check_password_hash(hashed_password, password):
    print("Password matches!")
else:
    print("Password does not match!")