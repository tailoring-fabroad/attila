-- name: is-user-following-for-another^
SELECT CASE
           WHEN following_id IS NULL THEN
               FALSE
           ELSE
               TRUE
           END AS is_following
FROM users u
         LEFT OUTER JOIN followers_to_followings f ON u.id = f.follower_id
    AND f.following_id = (
        SELECT id
        FROM users
        WHERE username = :following_username)
WHERE u.username = :follower_username
LIMIT 1;
