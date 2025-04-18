-- name: create-new-role<!
INSERT INTO roles (name) VALUES (:name) ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name RETURNING id;

-- name: create-new-user-to-role!
INSERT INTO users_to_roles (user_id, role_id) VALUES (:user_id, :role_id)
