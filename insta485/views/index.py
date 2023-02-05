"""
Insta485 index (main) view.

URLs include:
/
"""


import os
import hashlib
import pathlib
import uuid
import arrow
import flask
from flask import send_from_directory, url_for
import insta485


@insta485.app.route('/uploads/<imgs>')
def show_picture(imgs):
    """Image upload."""
    if 'username' not in flask.session:
        flask.abort(403)
    return send_from_directory(insta485.app.config['UPLOAD_FOLDER'], imgs)


@insta485.app.route('/')
def show_index():
    """Display / route."""
    # Connect to database
    if 'username' not in flask.session:
        return flask.redirect(url_for("login"))
    connection = insta485.model.get_db()
    logname = flask.session['username']
    logname_follows_username = False
    posts = connection.execute(
        "SELECT postid, filename, owner, created "
        "FROM posts "
        "WHERE owner IN "
        "(SELECT username2 FROM following WHERE username1 == ?) "
        "OR owner == ?"
        "ORDER BY postid DESC",
        (logname, logname)
    ).fetchall()

    all_users = connection.execute(
        "SELECT username , filename FROM users"
    ).fetchall()
    # owner_img_url
    # for i, number in enumerate(numbers):
    for post in posts:
        # get username
        get_user_name = post["owner"]
        utc = arrow.get(post["created"])
        utc.to('local')
        post["created"] = utc.humanize()
        post["filename"] = '/uploads/' + post['filename']
        for user in all_users:
            if get_user_name == user['username']:
                post['owner_img_url'] = '/uploads/' + \
                    user['filename']
    # get comments comments with owners name oldest at the top
    # belongs to which post?

    comments_ = connection.execute(
        "SELECT * FROM comments "
        "ORDER BY commentid ASC",
    ).fetchall()
    for post in posts:
        get_post_id = post["postid"]
        post["comments"] = []
        for comment in comments_:
            if get_post_id == comment['postid']:
                post["comments"] += \
                    [{"owner": comment
                        ["owner"], "text":comment["text"]}]

    likes = connection.execute(
        "SELECT owner,postid "
        "FROM likes"
    ).fetchall()
    for post in posts:
        post['likes'] = 0
        post['logname_like'] = False
        for like in likes:
            if like['postid'] == post["postid"]:
                post['likes'] += 1
            if like['postid'] == post['postid']\
                    and like['owner'] == logname:
                post['logname_like'] = True

    context = {"logname": logname,
               "logname_follows_username": logname_follows_username,
               "posts": posts}

    return flask.render_template("index.html", **context)


@insta485.app.route('/users/<username>/')
def show_user(username):
    """Display / route."""
    if 'username' not in flask.session:
        return flask.redirect(url_for("login"))
    connection = insta485.model.get_db()
    logname = flask.session['username']
    result = connection.execute(
        "SELECT fullname "
        "FROM users "
        "WHERE username == ?",
        (username, )
    ).fetchall()
    if len(result) == 0:
        return flask.abort(404)
    fullname = result[0]['fullname']
    # how many posts does the user have?
    posts = connection.execute(
        "SELECT postid, filename, owner, created "
        "FROM posts "
        "WHERE owner == ?",
        (username,)
    ).fetchall()
    for post in posts:
        post['filename'] = '/uploads/'+post['filename']
    total_posts = len(posts)
    # follower_number
    followers = connection.execute(
        "SELECT username1 "
        "FROM following "
        "WHERE username2 == ?",
        (username, )
    ).fetchall()
    follower_number = len(followers)
    # following, if the logged in user is following user_url_slug
    # include unfollow button
    # does the login person follow current user?
    login_following = connection.execute(
        "SELECT username2 "
        "FROM following "
        "WHERE username1 == ? and username2 == ?",
        (logname, username)
    ).fetchall()
    isfollowing = len(login_following) > 0
    user_following = connection.execute(
        "SELECT username2 "
        "FROM following "
        "WHERE username1 == ?",
        (username, )
    ).fetchall()

    user_following_num = len(user_following)
    context = {"posts": posts, "fullname": fullname,
               "logname": logname, "username": username,
               "follower_number": follower_number,
               "isfollowing": isfollowing,
               "user_following_num": user_following_num,
               "total_posts": total_posts}
    return flask.render_template("user.html", **context)


@insta485.app.route('/users/<username>/followers/')
def show_user_follower(username):
    """Display / route."""
    connection = insta485.model.get_db()
    if 'username' not in flask.session:
        return flask.redirect(url_for("login"))
    logname = flask.session['username']
    user_exist = connection.execute(
        "SELECT 1 "
        "FROM users "
        "WHERE username = ?",
        (username, )
    ).fetchall()
    if len(user_exist) == 0:
        return flask.abort(404)
    # who follows username?
    followers = connection.execute(
        "SELECT username1 "
        "FROM following "
        "WHERE username2 == ?",
        (username, )
    ).fetchall()
    # does the login person follow current user?
    # login person follow who？
    login_following = connection.execute(
        "SELECT username2 "
        "FROM following "
        "WHERE username1 == ?",
        (logname, )
    ).fetchall()
    login_following_list = [i['username2'] for
                            i in login_following]
    for follower in followers:
        follower["logname_follows_username"] = False
        if follower["username1"] in login_following_list:
            follower["logname_follows_username"] = True
    users = connection.execute(
        "SELECT username, filename "
        "FROM users"
    ).fetchall()
    for follower in followers:
        user_name = follower["username1"]
        for j in users:
            if user_name == j["username"]:
                follower["user_img_url"] = '/uploads/' + j["filename"]
    context = {"followers": followers,
               "logname": logname, "username": username}
    return flask.render_template("followers.html", **context)


@insta485.app.route('/users/<username>/following/')
def show_user_following(username):
    """Display / route."""
    connection = insta485.model.get_db()
    if 'username' not in flask.session:
        return flask.redirect(url_for("login"))
    logname = flask.session['username']
    user_exist = connection.execute(
        "SELECT 1 "
        "FROM users "
        "WHERE username = ?",
        (username, )
    ).fetchall()
    if len(user_exist) == 0:
        return flask.abort(404)
    following = connection.execute(
        "SELECT username2 "
        "FROM following "
        "WHERE username1 == ?",
        (username, )
    ).fetchall()
    # does the login person follow current user?
    login_following = connection.execute(
        "SELECT username2 "
        "FROM following "
        "WHERE username1 == ?",
        (logname, )
    ).fetchall()
    login_following_list = [i['username2']
                            for i in login_following]
    for follow in following:
        follow["logname_follows_username"] = False
        if follow["username2"] in login_following_list:
            follow["logname_follows_username"] = True
    users = connection.execute(
        "SELECT username, filename "
        "FROM users"
    ).fetchall()
    for follow in following:
        user_name = follow["username2"]
        for j in users:
            if user_name == j["username"]:
                follow["user_img_url"] = '/uploads/'+j["filename"]

    context = {"following": following,
               "logname": logname, "username": username}
    return flask.render_template("following.html", **context)


@insta485.app.route('/posts/<postid>/', methods=['GET'])
def show_posts_postid(postid):
    """Display / route."""
    if 'username' not in flask.session:
        return flask.redirect(url_for("login"))
    connection = insta485.model.get_db()
    logname = flask.session['username']
    post = connection.execute(
        "SELECT postid, filename, owner, created "
        "FROM posts "
        "WHERE postid == ?",
        (postid,)
    ).fetchall()
    img_url = '/uploads/' + post[0]["filename"]
    owner_img_fetch = connection.execute(
        "SELECT filename FROM users "
        "WHERE username == ?",
        (post[0]["owner"],)
    ).fetchall()
    owner_img_url = '/uploads/'+owner_img_fetch[0]["filename"]
    utc = arrow.get(post[0]["created"])
    utc.to('local')
    timestamp = utc.humanize()
    likes_list = connection.execute(
        "SELECT owner, postid "
        "FROM likes "
        "WHERE postid == ?",
        (postid,)
    ).fetchall()
    likes = len(likes_list)
    logname_like = False
    for i in likes_list:
        if i["owner"] == logname:
            logname_like = True

    comments = connection.execute(
        "SELECT owner, text, commentid "
        "FROM comments "
        "WHERE postid == ?",
        (postid,)
    ).fetchall()

    context = {"logname": logname, "img_url": img_url,
               "owner": post[0]["owner"],
               "owner_img_url": owner_img_url, "postid": postid,
               "timestamp": timestamp, "likes": likes, "comments": comments,
               "logname_like": logname_like}
    return flask.render_template("post.html", **context)


@insta485.app.route('/explore/')
def show_explore():
    """Display / route."""
    if 'username' not in flask.session:
        return flask.redirect(url_for("login"))
    connection = insta485.model.get_db()
    logname = flask.session['username']
    users = connection.execute(
        "SELECT username, filename FROM users "
    ).fetchall()
    for user in users:
        user["filename"] = \
            "/uploads/"+user["filename"]
    logname_follow = connection.execute(
        "SELECT username2 "
        "FROM following "
        "WHERE username1 == ?",
        (logname,)
    ).fetchall()
    not_following = []
    logname_follow_list = [i["username2"] for i in logname_follow]
    for i in users:
        if (i["username"] not in logname_follow_list and
                i["username"] != logname):
            not_following.append(
                {"username": i["username"], "user_img_url": i["filename"]})
    context = {"logname": logname, "not_following": not_following}
    return flask.render_template("explore.html", **context)


@insta485.app.route('/comments/', methods=['POST'])
def comments_delete():
    """Display / route."""
    connection = insta485.model.get_db()
    logname = flask.session['username']
    create_state = flask.request.form['operation']
    result = flask.request.args.get('target')
    if create_state == 'create':
        postid = int(flask.request.form['postid'])
        text = flask.request.form['text']
        if text == '' or text is None:
            flask.abort(400)
        else:
            cur = connection.execute(
                "INSERT INTO comments(owner,postid,text) VALUES"
                "(?,?,?)",
                (logname, postid, text)
            )
    if create_state == 'delete':
        commentid = int(flask.request.form['commentid'])
        cur = connection.execute(
            "SELECT owner FROM comments "
            "WHERE commentid == ?",
            (commentid,)
        )
        owner = cur.fetchall()[0]["owner"]
        if owner != logname:
            flask.abort(403)
        else:
            cur = connection.execute(
                "DELETE FROM comments "
                "WHERE commentid == ?",
                (commentid,)
            )
    if result is None:
        return flask.redirect(url_for("show_index"))
    return flask.redirect(result)


# http://localhost:8000/likes/?target=explore
@insta485.app.route('/likes/', methods=['POST'])
def likes_delete():
    """Display / route."""
    connection = insta485.model.get_db()
    logname = flask.session['username']
    like = flask.request.form['operation']
    result = flask.request.args.get('target')
    postid_str = flask.request.form['postid']
    postid = int(postid_str)
    if like == 'like':
        # check already liked:
        check_already_liked = connection.execute(
            "SELECT owner from likes "
            "WHERE postid == ? and owner == ?",
            (postid, logname)
        ).fetchall()
        if len(check_already_liked) >= 1:
            return flask.abort(409)
        connection.execute(
            "INSERT INTO likes(owner,postid) VALUES"
            "(?,?)",
            (logname, postid)
        )
    else:
        check_already_unliked = connection.execute(
            "SELECT owner from likes "
            "WHERE postid == ? and owner == ?",
            (postid, logname)
        ).fetchall()
        if len(check_already_unliked) == 0:
            return flask.abort(409)
        # If operation is unlike, delete a like for postid.
        connection.execute(
            "DELETE FROM likes "
            "WHERE postid == ? and owner == ?",
            (postid, logname)
        )
    if result is None:
        return flask.redirect(url_for("show_index"))
    return flask.redirect(result)


@insta485.app.route('/following/', methods=['POST'])
def follow_delete():
    """Display / route."""
    connection = insta485.model.get_db()
    follow = flask.request.form['operation']
    username = flask.request.form['username']
    result = flask.request.args.get('target')
    logname = flask.session['username']
    if follow == 'follow':
        # If operation is follow, then make user logname follow user username.
        # follow a user that they already follow, then abort(409).
        cur = connection.execute(
            "SELECT * from following "
            "WHERE username1 == ? and username2 == ?",
            (logname, username)
        )
        return_follow = cur.fetchall()
        if len(return_follow) == 0:
            cur = connection.execute(
                "INSERT INTO following(username1,username2) VALUES"
                "(?,?)",
                (logname, username)
            )
        else:
            flask.abort(409)
    else:
        return_follow = connection.execute(
            "SELECT * from following "
            "WHERE username1 == ? and username2 == ?",
            (logname, username)
        ).fetchall()
        if len(return_follow) >= 1:
            cur = connection.execute(
                "DELETE FROM following "
                "WHERE username1 == ? and username2 == ?",
                (logname, username)
            )
        else:
            flask.abort(409)
    if result is None:
        return flask.redirect(url_for("show_index"))
    return flask.redirect(result)


@insta485.app.route('/posts/', methods=['POST'])
def post_delete():
    """Display / route."""
    connection = insta485.model.get_db()
    operation = flask.request.form['operation']
    result = flask.request.args.get('target')
    logname = flask.session['username']
    # where to get the img???? save to disk?
    #  save to the folder --> var/upload ...???
    if operation == 'create':
        fileobj = flask.request.files["file"]
        # Unpack flask object
        filename = fileobj.filename
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if filename == '':
            flask.abort(400)
        else:
            uuid_basename = compute_filename_save()
            cur = connection.execute(
                "INSERT INTO posts "
                "(filename,owner) VALUES "
                "(?,?)",
                (uuid_basename, logname)
            )
    if operation == 'delete':
        # delete a post they not own
        postid_state = flask.request.form['postid']
        postid = int(postid_state)
        cur = connection.execute(
            "SELECT postid, owner FROM posts "
            "WHERE postid == ?",
            (postid,)
        )
        result_fetched = cur.fetchall()
        person_who_post = result_fetched[0]["owner"]
        # logname = "jag"
        if person_who_post != logname:
            flask.abort(403)
        else:
            delete_img = connection.execute(
                "SELECT filename FROM posts "
                "WHERE postid == ?",
                (postid,)
            ).fetchall()
            cur = connection.execute(
                "DELETE FROM posts "
                "WHERE postid == ?",
                (postid,)
            )
            # 因为是Foreign key
            # cur = connection.execute(
            #     "DELETE FROM likes "
            #     "WHERE postid == ?",
            #     (postid,)
            # )
            # cur = connection.execute(
            #     "DELETE FROM comments "
            #     "WHERE postid == ?",
            #     (postid,)
            # )
            # remove post from the os
            path = os.path.join(
                insta485.app.config["UPLOAD_FOLDER"],
                delete_img[0]["filename"])
            os.remove(path)

    if result is None:
        # ？？？？ test here
        return flask.redirect(url_for("show_user", username=logname))
    return flask.redirect(result)


def hashed_password_generate(input_older_password):
    """Display / route."""
    algorithm = 'sha512'
    salt = uuid.uuid4().hex
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + input_older_password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])
    return password_db_string


def hashed_password_ping(input_older_password, salt):
    """Display / route."""
    algorithm = 'sha512'
    # salt = uuid.uuid4().hex
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + input_older_password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])
    return password_db_string


def compute_filename_save():
    """Display / route."""
    fileobj = flask.request.files["file"]
    filename = fileobj.filename
    stem = uuid.uuid4().hex
    suffix = pathlib.Path(filename).suffix.lower()
    uuid_basename = f"{stem}{suffix}"
    path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
    fileobj.save(path)
    return uuid_basename


# http://localhost:8000/accounts/login/
@insta485.app.route('/accounts/login/')
def login():
    """Display / route."""
    if 'username' in flask.session:
        return flask.redirect(flask.url_for('show_index'))
    return flask.render_template("login.html")


@insta485.app.route('/accounts/logout/', methods=['POST'])
def logout():
    """Display / route."""
    flask.session.clear()
    return flask.redirect(flask.url_for('login'))


@insta485.app.route('/accounts/create/', methods=['GET'])
def create():
    """Display / route."""
    if 'username' in flask.session:
        return flask.redirect(flask.url_for('edit'))
    return flask.render_template('create.html')


@insta485.app.route('/accounts/delete/', methods=['GET'])
def delete():
    """Display / route."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login'))
    logname = flask.session['username']
    context = {"logname": logname}
    return flask.render_template('delete.html', **context)


@insta485.app.route('/accounts/edit/', methods=['GET'])
def edit():
    """Display / route."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login'))
    connection = insta485.model.get_db()
    logname = flask.session['username']
    result = connection.execute("SELECT * from users").fetchall()
    result = connection.execute(
        "SELECT * FROM users WHERE "
        "username == ?",
        (logname,)
    ).fetchall()[0]
    fullname = result["fullname"]
    email = result["email"]
    context = {"logname": logname,
               "email_address": email, "fullname": fullname}
    return flask.render_template('edit.html', **context)


@insta485.app.route('/accounts/password/', methods=['GET'])
def password():
    """Display / route."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login'))
    logname = flask.session['username']
    context = {"logname": logname}
    return flask.render_template('password.html', **context)


def check_password(input_older_password, real_older_password):
    """Display / route."""
    salt = real_older_password.split('$')[1]
    input_older_password = hashed_password_ping(input_older_password, salt)
    return real_older_password == input_older_password


def login_helper():
    """Display / route."""
    connection = insta485.model.get_db()
    username = flask.request.form['username']
    input_password = flask.request.form['password']

    if username is not None and input_password is not None and username != ''\
            and input_password != '':
        user_info = connection.execute(
            "SELECT * FROM users "
            "WHERE username = ?;",
            (username,)
        ).fetchall()
        if user_info is None:
            return flask.abort(403)
        # 1. user does not exist
        if len(user_info) == 0:
            return flask.abort(403)
        # 2. user exist but the password does not match
        password_database = user_info[0]["password"]
        input_password_check = check_password(input_password,
                                              password_database)
        if input_password_check is False:
            return flask.abort(403)

        flask.session.clear()
        flask.session['username'] = username
        if flask.request.args.get('target') is None:
            return flask.redirect(flask.url_for('show_index'))
        return flask.redirect(flask.request.args.get('target'))

    return flask.abort(400)


def create_helper():
    """Display / route."""
    username = flask.request.form['username']
    input_password = flask.request.form['password']
    input_password = hashed_password_generate(input_password)
    fullname = flask.request.form['fullname']
    email = flask.request.form['email']
    fileobj = flask.request.files["file"]
    filename = fileobj.filename
    connection = insta485.model.get_db()
    if (username or input_password or fullname or email or filename) is None:
        return flask.abort(400)
    filename = compute_filename_save()
    try:
        connection.execute(
            "INSERT INTO users "
            "(username, fullname, email, filename, password) "
            "VALUES (?, ?, ?, ?, ?)",
            (username, fullname, email, filename, input_password)
        )
        connection.commit()
        flask.session['username'] = flask.request.form['username']
    except connection.IntegrityError:
        return flask.abort(409)
    if flask.request.args.get('target') is None:
        return flask.redirect(flask.url_for('show_index'))
    return flask.redirect(flask.request.args.get('target'))


def delete_helper():
    """Display / route."""
    if 'username' not in flask.session:
        return flask.abort(403)
    username = flask.session['username']
    connection = insta485.model.get_db()
    go_to = flask.request.args.get('target')
    posts = connection.execute(
        "SELECT filename "
        "FROM posts "
        "WHERE owner = ?",
        (username, )
    ).fetchall()
    for post in posts:
        path = os.path.join(
            insta485.app.config["UPLOAD_FOLDER"], post["filename"])
        os.remove(path)
    user_icons = connection.execute(
        "SELECT filename "
        "FROM users "
        "WHERE username = ?",
        (username, )
    ).fetchall()
    for icon in user_icons:
        path = os.path.join(
            insta485.app.config["UPLOAD_FOLDER"], icon["filename"])
        os.remove(path)
    connection.execute(
        "DELETE FROM users "
        "WHERE username = ?",
        (username, )
    )
    connection.commit()
    flask.session.clear()
    if go_to is None:
        return flask.redirect(flask.url_for('show_index'))
    return flask.redirect(go_to)


def edit_account_helper():
    """Display / route."""
    if 'username' not in flask.session:
        return flask.abort(403)
    connection = insta485.model.get_db()
    username = flask.session['username']
    edit_fullname = flask.request.form['fullname']
    edit_email = flask.request.form['email']
    file = flask.request.files["file"]
    if edit_fullname is None or edit_fullname == '' \
            or edit_email is None or edit_email == "":
        return flask.abort(400)
    # check if photo file is included
    if file.filename == '':
        connection.execute(
            "UPDATE users "
            "SET fullname= ? , "
            "email=? "
            "WHERE  username=?",
            (edit_fullname, edit_email, username, )
        )
    else:
        prev_image = connection.execute(
            "SELECT filename "
            "FROM users "
            "WHERE username=?",
            (username, )
        ).fetchall()
        path = os.path.join(
            insta485.app.config["UPLOAD_FOLDER"], prev_image[0]["filename"])
        os.remove(path)
        new_img = compute_filename_save()
        connection.execute(
            "UPDATE users "
            "SET fullname=?, "
            "email=?, "
            "filename=? "
            "WHERE username=?",
            (edit_fullname, edit_email, new_img, username))
    if flask.request.args.get('target') is None:
        return flask.redirect(flask.url_for('show_index'))
    return flask.redirect(flask.request.args.get('target'))


def update_password_helper():
    """Display / route."""
    if 'username' not in flask.session:
        return flask.abort(403)
    user_name = flask.session['username']
    connection = insta485.model.get_db()
    context = connection.execute(
        "SELECT password "
        "FROM users "
        "WHERE username = ?",
        (user_name,)
    ).fetchone()
    real_older_password = context.get('password')
    salt = real_older_password.split('$')[1]
    input_older_password = flask.request.form['password']
    input_older_password = hashed_password_ping(input_older_password, salt)
    if real_older_password != input_older_password:
        return flask.abort(403)

    new_password1 = flask.request.form['new_password1']
    new_password2 = flask.request.form['new_password2']
    if new_password1 != new_password2:
        return flask.abort(401)
    hash_password = hashed_password_generate(new_password1)
    connection.execute("UPDATE users "
                       "SET password = ? "
                       "WHERE username = ?",
                       (hash_password, user_name))
    if flask.request.args.get('target') is None:
        return flask.redirect(flask.url_for('show_index'))
    return flask.redirect(flask.request.args.get('target'))


@insta485.app.route('/accounts/', methods=['POST'])
def account_operation():
    """Display / route."""
    operation = flask.request.form['operation']
    if operation == 'login':
        login_helper()
    elif operation == 'create':
        create_helper()
    elif operation == 'delete':
        delete_helper()
    elif operation == 'edit_account':
        edit_account_helper()
    elif operation == 'update_password':
        update_password_helper()

    if flask.request.args.get('target') is None:
        return flask.redirect(flask.url_for('show_index'))
    return flask.redirect(flask.request.args.get('target'))
