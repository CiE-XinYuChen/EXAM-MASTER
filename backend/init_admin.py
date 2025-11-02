"""
Initialize admin user directly in database
"""

import sqlite3
from app.core.security import get_password_hash

def create_admin():
    # Connect to database
    conn = sqlite3.connect('databases/main.db')
    cursor = conn.cursor()

    # Check if admin exists
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    existing_admin = cursor.fetchone()

    if existing_admin:
        print("Admin user already exists. Updating password...")
        # Update the password hash to use the new pre-hashing mechanism
        password_hash = get_password_hash("admin123")
        cursor.execute("""
            UPDATE users
            SET password_hash = ?, updated_at = datetime('now')
            WHERE username = 'admin'
        """, (password_hash,))
        conn.commit()
        conn.close()
        print("Admin password updated successfully!")
        print("Username: admin")
        print("Password: admin123")
        return

    # Create admin user
    password_hash = get_password_hash("admin123")

    cursor.execute("""
        INSERT INTO users (username, email, password_hash, role, is_active, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'))
    """, ('admin', 'admin@example.com', password_hash, 'admin', 1))

    conn.commit()
    conn.close()

    print("Admin user created successfully!")
    print("Username: admin")
    print("Password: admin123")

if __name__ == "__main__":
    create_admin()