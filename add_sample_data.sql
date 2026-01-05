-- Sample data for users table
INSERT INTO users (email, custom_id, name, picture, role, credits) VALUES
    ('byoungikhwang@gmail.com', 'admin_id', 'Admin User', 'https://example.com/admin_pic.jpg', 'ADMIN', 100)
ON CONFLICT (email) DO UPDATE SET
    custom_id = EXCLUDED.custom_id,
    name = EXCLUDED.name,
    picture = EXCLUDED.picture,
    role = EXCLUDED.role,
    credits = EXCLUDED.credits;

-- Sample data for media table
INSERT INTO media (user_id, title, description, media_type, url, hashtags) VALUES
    ((SELECT id FROM users WHERE email = 'byoungikhwang@gmail.com'), 'Admin Image 1', 'First image from admin.', 'image', '/static/uploads/admin_image_01.png', ARRAY['#admin', '#first_upload']),
    ((SELECT id FROM users WHERE email = 'byoungikhwang@gmail.com'), 'Admin Video 1', 'First video from admin, very popular!', 'video', '/static/uploads/admin_video_01.mp4', ARRAY['#admin', '#video', '#popular']),
    ((SELECT id FROM users WHERE email = 'byoungikhwang@gmail.com'), 'User Image 1', 'A beautiful photo by test user.', 'image', '/static/uploads/user_image_01.png', ARRAY['#user', '#nature']),
    ((SELECT id FROM users WHERE email = 'byoungikhwang@gmail.com'), 'User Video 1', 'Test user''s awesome clip.', 'video', '/static/uploads/user_video_01.mp4', ARRAY['#user', '#clip'])
ON CONFLICT DO NOTHING;

-- Sample data for media_likes table
INSERT INTO media_likes (user_id, media_id) VALUES
    ((SELECT id FROM users WHERE email = 'byoungikhwang@gmail.com'), (SELECT id FROM media WHERE title = 'Admin Image 1')),
    ((SELECT id FROM users WHERE email = 'byoungikhwang@gmail.com'), (SELECT id FROM media WHERE title = 'Admin Video 1')),
    ((SELECT id FROM users WHERE email = 'byoungikhwang@gmail.com'), (SELECT id FROM media WHERE title = 'User Image 1')),
    ((SELECT id FROM users WHERE email = 'byoungikhwang@gmail.com'), (SELECT id FROM media WHERE title = 'User Video 1'));

INSERT INTO media_likes (user_id, media_id) VALUES
    ((SELECT id FROM users WHERE email = 'byoungikhwang@gmail.com'), (SELECT id FROM media WHERE title = 'Admin Video 1'))
ON CONFLICT DO NOTHING;
