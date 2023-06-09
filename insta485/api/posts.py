"""REST API for posts."""
import flask
import insta485


@insta485.app.route('/api/v1/', methods=["GET"])
def get_services():
    """Get basic pages."""
    # Return a list of services available. The output
    # should look exactly like this example.
    # Does not require user to be authenticated.
    context = {
        "comments": "/api/v1/comments/",
        "likes": "/api/v1/likes/",
        "posts": "/api/v1/posts/",
        "url":  flask.request.full_path[:-1]
    }
    print(context)
    return flask.jsonify(**context), 200


@insta485.app.route('/api/v1/posts/', methods=["GET"])
def get_post():
    """Get whole index page."""
    # Return the 10 newest posts.
    # each post is made by a user which the logged in user follows
    # or the post is made by the logged in user.
    # When postid_lte is not specified, default to the most recent postid
    auth = flask.request.authorization
    if 'username' not in flask.session and not auth:
        flask.abort(403)
    logname = flask.session.get('username')
    if not logname:
        logname = flask.request.authorization['username']
        password = flask.request.authorization['password']
        if not logname or not password:
            return flask.jsonify({}), 400
    size = flask.request.args.get("size", default=10, type=int)
    page = flask.request.args.get("page", default=0, type=int)
    postid_if_user = flask.request.args.get("postid_lte", None)
    if size < 0 or page < 0:
        return flask.jsonify({}), 400
    connection = insta485.model.get_db()
    total_post = connection.execute(
        "SELECT postid FROM posts "
        "where owner == ? OR "
        "owner IN (SELECT username2 FROM following "
        "where username1 == ?)",
        (logname, logname, )
    ).fetchall()
    new = total_post[len(total_post)-1]['postid']
    # if postid_lte is not specified
    if postid_if_user is None:
        selected_postid = connection.execute(
            "SELECT postid,  ('/api/v1/posts/' || postid ||\
                 '/') AS url FROM posts "
            "where owner == ? OR "
            "owner IN (SELECT username2 FROM following "
            "where username1 == ?) ORDER BY postid DESC "
            "LIMIT ? OFFSET ?",
            (logname, logname, size, size*page,)
        ).fetchall()
        results = list(selected_postid)
        n_e = ""
        if size*(page+1) <= len(total_post):
            n_e = f"/api/v1/posts/?size={size}&page={page+1}&postid_lte={new}"
    #  if specified
    else:
        selected = connection.execute(
            "SELECT postid,  ('/api/v1/posts/' || postid ||\
                 '/') AS url FROM posts "
            "where (owner == ? OR "
            "owner IN (SELECT username2 FROM following "
            "where username1 == ?)) "
            "AND postid < ? ORDER BY postid DESC ",
            (logname, logname, postid_if_user,)
        ).fetchall()
        results = []
        for i in selected:
            if int(postid_if_user)-size*page >= 0:
                if int(i['postid']) <= int(postid_if_user)-size*page:
                    results.append(i)
        if size*(page+1) + 1 <= len(total_post):
            n_e = f"/api/v1/posts/?size={size}&page={page+1}&postid_lte={new}"
        else:
            n_e = ""
    context = {
        "next": n_e,
        "results": results,
        "url": flask.request.full_path.rstrip("?"),
    }
    return flask.jsonify(**context), 200


def check_help():
    """Help function."""
    if 'username' not in flask.session and not flask.request.authorization:
        flask.abort(403)


@insta485.app.route('/api/v1/posts/<int:postid_url_slug>/', methods=['GET'])
def get_post1(postid_url_slug):
    """Get information of a single post."""
    # checking authorization...
    check_help()
    username = flask.session.get('username')
    if not username:
        username = flask.request.authorization['username']
        if not username or not flask.request.authorization['password']:
            return flask.jsonify({}), 400

    # get post info from db
    largest = insta485.model.get_db().execute(
        "SELECT postid FROM posts"
    ).fetchall()
    if postid_url_slug > largest[len(largest)-1]['postid']:
        return flask.jsonify({}), 404
    post = insta485.model.get_db().execute(
        "SELECT filename,owner,created FROM posts "
        "WHERE postid=?",
        (postid_url_slug, )
    ).fetchone()

    # get post owner info from db
    curr = insta485.model.get_db().execute(
        "SELECT filename FROM users "
        "WHERE username=?",
        (post['owner'], )
    )

    # get comment info from db
    allcomment = insta485.model.get_db().execute(
        "SELECT * FROM comments "
        "WHERE postid=?",
        (postid_url_slug, )
    ).fetchall()
    comments_list = []
    for comment in allcomment:
        singlecommen = {}
        singlecommen['commentid'] = comment['commentid']
        singlecommen['owner'] = comment['owner']
        singlecommen['lognameOwnsThis'] = False
        if comment['owner'] == username:
            singlecommen['lognameOwnsThis'] = True
        singlecommen['ownerShowUrl'] = f"/users/{comment['owner']}/"
        singlecommen['text'] = comment['text']
        singlecommen['url'] = f"/api/v1/comments/{singlecommen['commentid']}/"
        comments_list.append(singlecommen)

    # get post being liked condition from db

    like_condition = insta485.model.get_db().execute(
        "SELECT * FROM likes "
        "WHERE postid=?",
        (postid_url_slug, )
    ).fetchall()
    likes_dict = {}
    if len(like_condition) == 0:
        likes_dict['url'] = None
        likes_dict['lognameLikesThis'] = False
        likes_dict['numLikes'] = 0
    else:
        login_user_liked = False
        for likes in like_condition:
            if username == likes['owner']:
                login_user_liked = True
        if login_user_liked:
            likes_dict['url'] = f"/api/v1/likes/{like_condition[0]['likeid']}/"
        else:
            # If the logged in user does not like the post
            # then the like url should be null
            likes_dict['url'] = None
        likes_dict['lognameLikesThis'] = login_user_liked
        likes_dict['numLikes'] = len(like_condition)

    # assemble information into the context dictionary
    context = {}
    context['comments'] = comments_list
    context['comments_url'] = f"/api/v1/comments/?postid={postid_url_slug}"
    context['created'] = post['created']
    context['imgUrl'] = '/uploads/' + post['filename']
    context['likes'] = likes_dict
    context['owner'] = post['owner']
    context['ownerImgUrl'] = '/uploads/' + curr.fetchone()['filename']
    context['ownerShowUrl'] = f"/users/{post['owner']}/"
    context['postShowUrl'] = f"/posts/{postid_url_slug}/"
    context['postid'] = postid_url_slug
    context['url'] = flask.request.path

    return flask.jsonify(**context)


@insta485.app.route('/api/v1/likes/', methods=['POST'])
def create_like():
    """Create a like for a post."""
    # checking authorization...
    auth = flask.request.authorization
    if 'username' not in flask.session and not auth:
        flask.abort(403)
    username = flask.session.get('username')
    if not username:
        username = flask.request.authorization['username']
        password = flask.request.authorization['password']
        if not username or not password:
            return flask.jsonify({}), 400

    # initializing context dictionary
    context = {}

    # getting post id
    postid = flask.request.args.get('postid')

    # check if the like is already existing
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT * FROM likes "
        "WHERE postid == ?"
        "AND owner = ?",
        (postid, username)
    )
    checking_likes = cur.fetchall()
    if len(checking_likes) != 0:
        # If the “like” already exists,
        # return the like object with a 200 response.
        likeid = checking_likes[0]['likeid']
        url = f"/api/v1/likes/{likeid}/"
        context['likeid'] = likeid
        context['url'] = url
        return flask.jsonify(**context), 200

    # Create one “like” for a specific post. Return 201 on success.
    connection.execute(
        "INSERT INTO likes(owner,postid) VALUES"
        "(?,?)",
        (username, postid)
    )
    find_new_like = connection.execute(
        "SELECT * FROM likes "
        "WHERE postid == ? and owner == ?",
        (postid, username)
    )
    like_id = find_new_like.fetchone()['likeid']
    url = f"/api/v1/likes/{like_id}/"
    context['likeid'] = like_id
    context['url'] = url
    return flask.jsonify(**context), 201


# DELETE /api/v1/likes/<likeid>/
@insta485.app.route('/api/v1/likes/<likeid>/', methods=['DELETE'])
def delete_like(likeid):
    """Delete a like for a post."""
    auth = flask.request.authorization
    if 'username' not in flask.session and not auth:
        flask.abort(403)
    username = flask.session.get('username')
    if not username:
        username = flask.request.authorization['username']
        password = flask.request.authorization['password']
        if not username or not password:
            return flask.jsonify({}), 400

    # check if the like is already existing
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT * FROM likes "
        "WHERE likeid == ?"
        "AND owner = ?",
        (likeid, username)
    )
    user_own_like = cur.fetchall()
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT * FROM likes "
        "WHERE likeid == ?",
        (likeid,)
    )
    likeid_exist = cur.fetchall()
    if len(likeid_exist) == 0:
        # If the likeid does not exist, return 404.
        return flask.jsonify({}), 404
    if len(user_own_like) == 0:
        # If the user does not own the like, return 403.
        return flask.jsonify({}), 403

    # Delete one “like”. Return 204 on success.
    connection.execute(
        "DELETE FROM likes "
        "WHERE likeid == ? and owner == ?",
        (likeid, username)
    )
    connection.commit()
    return flask.jsonify({}), 204


@insta485.app.route('/api/v1/comments/', methods=['POST'])
def create_comment():
    """Create a comment."""
    auth = flask.request.authorization
    if 'username' not in flask.session and not auth:
        flask.abort(403)
    username = flask.session.get('username')
    if not username:
        username = flask.request.authorization['username']
        password = flask.request.authorization['password']
        if not username or not password:
            return flask.jsonify({}), 400
    # initializing context dictionary
    context = {}
    # get postid from url
    postid = flask.request.args.get('postid')
    # HINT: sqlite3 provides a special function to retrieve
    #  the ID of the most recently inserted item: SELECT last_insert_rowid().
    connection = insta485.model.get_db()

    text = flask.request.get_json()['text']

    connection = insta485.model.get_db()
    cur = connection.execute(
        "INSERT INTO comments(owner,postid,text) VALUES"
        "(?,?,?)",
        (username, postid, text)
    )

    cur = connection.execute(
        # 如果一个表中有 INTEGER PRIMARY KEY 列，则该列变成 ROWID 的别名。
        # the database is comments, so the primary key is comment id
        "SELECT last_insert_rowid()"
    )
    new_comment_id = cur.fetchall()[0]['last_insert_rowid()']

    commentid = new_comment_id
    context['commentid'] = commentid
    context['lognameOwnsThis'] = True
    context['owner'] = username
    context['text'] = text
    context['url'] = f"/api/v1/comments/{commentid}/"
    context['ownerShowUrl'] = f"/users/{username}/"

    return flask.jsonify(**context), 201


# DELETE /api/v1/comments/<commentid>/
@insta485.app.route('/api/v1/comments/<commentid>/', methods=['DELETE'])
def delete_comment(commentid):
    """Delete a comment."""
    auth = flask.request.authorization
    if 'username' not in flask.session and not auth:
        flask.abort(403)
    username = flask.session.get('username')
    if not username:
        username = flask.request.authorization['username']
        password = flask.request.authorization['password']
        if not username or not password:
            return flask.jsonify({}), 400
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT owner FROM comments "
        "WHERE commentid == ?",
        (commentid,)
    )
    comment_id_exist = cur.fetchall()
    if len(comment_id_exist) == 0:
        # If the commentid does not exist, return 404.
        return flask.jsonify({}), 404

    # If the user doesn’t own the comment, return 403.
    owner = comment_id_exist[0]["owner"]
    if owner != username:
        return flask.jsonify({}), 403

    # Delete a comment. Include the ID of the comment in the URL.
    # Return 204 on success.
    connection.execute(
        "DELETE FROM comments "
        "WHERE commentid == ?",
        (commentid,)
    )
    connection.commit()
    return flask.jsonify({}), 204
