"""REST API for posts."""
import flask
import insta485

@insta485.app.route('/api/v1/', methods=["GET"])
def get_services():
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
    # size_if_user = flask.request.args.get("size", None)
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
    numPost = len(total_post)
    newest = total_post[numPost-1]['postid']
    # if postid_lte is not specified
    if (postid_if_user is None):
        # postid_if_user = flask.request.args.get("page"
        selected_postid = connection.execute(
            "SELECT postid,  ('/api/v1/posts/' || postid || '/') AS url FROM posts "
            "where owner == ? OR "
            "owner IN (SELECT username2 FROM following "
            "where username1 == ?) ORDER BY postid DESC "
            "LIMIT ? OFFSET ?",
            (logname, logname, size, size*page,)
        ).fetchall()
        results = list(selected_postid)
        if size*(page+1) <= numPost:
            # ?????????what is the page (the max)
            next = "/api/v1/posts/?size={}&page={}&postid_lte={}".format(size, page+1,newest)
        else:
            next = ""
    #  if specified
    else:
        selected = connection.execute(
            "SELECT postid,  ('/api/v1/posts/' || postid || '/') AS url FROM posts "
            "where (owner == ? OR "
            "owner IN (SELECT username2 FROM following "
            "where username1 == ?)) "
            "AND postid < ? ORDER BY postid DESC ",
            (logname, logname, postid_if_user,)
        ).fetchall()
        results = []
        for id in selected:
            if int(postid_if_user)-size*page >= 0:
                if int(id['postid']) <= int(postid_if_user)-size*page:
                    results.append(id)
        if size*(page+1) + 1 <= numPost:
            next = "/api/v1/posts/?size={}&page={}&postid_lte={}".format(size, page+1,newest)
        else:
            next = ""
    context = {
        "next": next,
        "results": results,
        "url": flask.request.full_path.rstrip("?"),
    }
    return flask.jsonify(**context), 200


@insta485.app.route('/api/v1/posts/<int:postid_url_slug>/', methods=['GET'])
def get_post1(postid_url_slug):
    #checking authorization...
    auth = flask.request.authorization
    if 'username' not in flask.session and not auth:
        flask.abort(403)
    username = flask.session.get('username')
    if not username:
        username = flask.request.authorization['username']
        password = flask.request.authorization['password']
        if not username or not password:
            return flask.jsonify({}), 400

    #get post info from db
    connection = insta485.model.get_db()
    largest = connection.execute(
        "SELECT postid "
        "FROM posts"
    ).fetchall()
    numPost = len(largest)
    newest = largest[numPost-1]['postid']
    if postid_url_slug > newest:
        return flask.jsonify({}), 404
    cur = connection.execute(
        "SELECT filename,owner,created FROM posts "
        "WHERE postid=?",
        (postid_url_slug, )
    )
    post = cur.fetchone()
    filename = '/uploads/' + post['filename']
    owner = post['owner']

    #get post owner info from db
    cur = connection.execute(
        "SELECT filename FROM users "
        "WHERE username=?",
        (owner, )
    )
    userimage = '/uploads/' + cur.fetchone()['filename']
    ownerurl = "/users/{}/".format(owner)

    #get comment info from db
    cur = connection.execute(
        "SELECT * FROM comments "
        "WHERE postid=?",
        (postid_url_slug, )
    )
    allcomment = cur.fetchall()
    comments_list = []
    for comment in allcomment:
        loguser_create_this_comment = False
        singlecomment = {}
        singlecomment['commentid'] = comment['commentid']
        singlecomment['owner'] = comment['owner']
        #print(flask.session.get('username'))
        if(comment['owner'] == username):
            loguser_create_this_comment = True
        singlecomment['lognameOwnsThis'] = loguser_create_this_comment
        ownerurl = "/users/{}/".format(comment['owner'])
        singlecomment['ownerShowUrl'] = ownerurl
        singlecomment['text'] = comment['text']
        comment_url = "/api/v1/comments/{}/".format(singlecomment['commentid'])
        singlecomment['url'] = comment_url
        comments_list.append(singlecomment)

    #get post being liked condition from db
    cur = connection.execute(
        "SELECT * FROM likes "
        "WHERE postid=?",
        (postid_url_slug, )
    )
    like_condition = cur.fetchall()
    likes_dict = {}
    if(len(like_condition) == 0):
        numlikes = 0
        login_user_liked = False
        like_url = None
        likes_dict['url'] = like_url
        likes_dict['lognameLikesThis'] = login_user_liked
        likes_dict['numLikes'] = numlikes
    else:
        numlikes = len(like_condition)
        login_user_liked = False
        like_id = like_condition[0]['likeid']
        for likes in like_condition:
            if username == likes['owner']:
                login_user_liked = True
        if login_user_liked:
            like_url = "/api/v1/likes/{}/".format(like_id)
        else:
            #If the logged in user does not like the post
            #then the like url should be null
            like_url = None
        likes_dict['url'] = like_url
        likes_dict['lognameLikesThis'] = login_user_liked
        likes_dict['numLikes'] = numlikes

    #assemble information into the context dictionary
    context = {}
    context['comments'] = comments_list
    context['comments_url'] = "/api/v1/comments/?postid={}".format(postid_url_slug)
    context['created'] = post['created']
    context['imgUrl'] = filename
    context['likes'] = likes_dict
    context['owner'] = post['owner']
    context['ownerImgUrl'] = userimage
    context['ownerShowUrl'] = "/users/{}/".format(owner)
    context['postShowUrl'] = "/posts/{}/".format(postid_url_slug)
    context['postid'] = postid_url_slug
    context['url'] = flask.request.path

    return flask.jsonify(**context)


@insta485.app.route('/api/v1/likes/', methods=['POST'])
def create_like():
    #checking authorization...
    auth = flask.request.authorization
    if 'username' not in flask.session and not auth:
        flask.abort(403)
    username = flask.session.get('username')
    if not username:
        username = flask.request.authorization['username']
        password = flask.request.authorization['password']
        if not username or not password:
            return flask.jsonify({}), 400
    
    #initializing context dictionary
    context = {}

    #getting post id
    postid = flask.request.args.get('postid')

    #check if the like is already existing
    connection = insta485.model.get_db()
    cur = connection.execute(
            "SELECT * FROM likes "
            "WHERE postid == ?"
            "AND owner = ?",
            (postid, username)
        )
    checking_likes = cur.fetchall()
    if(len(checking_likes) != 0):
        #If the “like” already exists, 
        #return the like object with a 200 response.
        likeid = checking_likes[0]['likeid']
        url = "/api/v1/likes/{}/".format(likeid)
        context['likeid'] = likeid
        context['url'] = url
        return flask.jsonify(**context), 200
    else:
        #Create one “like” for a specific post. Return 201 on success.
        connection.execute(
                "INSERT INTO likes(owner,postid) VALUES"
                "(?,?)",
                (username, postid)
            )
        find_new_like = connection.execute(
                "SELECT * FROM likes "
                "WHERE postid == ?",
                (postid, )
            )
        like_id = find_new_like.fetchone()['likeid']
        url = "/api/v1/likes/{}/".format(like_id)
        print("created ",url)
        context['likeid'] = like_id
        context['url'] = url
        return flask.jsonify(**context), 201


# DELETE /api/v1/likes/<likeid>/
@insta485.app.route('/api/v1/likes/<likeid>/',methods=['DELETE'])
def delete_like(likeid):
    auth = flask.request.authorization
    if 'username' not in flask.session and not auth:
        flask.abort(403)
    username = flask.session.get('username')
    if not username:
        username = flask.request.authorization['username']
        password = flask.request.authorization['password']
        if not username or not password:
            return flask.jsonify({}), 400
    #check if the like is already existing
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
    if(len(likeid_exist) == 0):
        # If the likeid does not exist, return 404.
        return flask.jsonify({}), 404
    elif(len(user_own_like) == 0):
        # If the user does not own the like, return 403.
        return flask.jsonify({}), 403
    else:
        # Delete one “like”. Return 204 on success.
        connection.execute(
            "DELETE FROM likes "
            "WHERE likeid == ? and owner == ?",
            (likeid, username)
        )
        connection.commit()
        print("deleted ",likeid)
        return flask.jsonify({}), 204


@insta485.app.route('/api/v1/comments/', methods=['POST'])
def create_comment():
    auth = flask.request.authorization
    """return create comment """
    if 'username' not in flask.session and not auth:
        flask.abort(403)
    username = flask.session.get('username')
    if not username:
        username = flask.request.authorization['username']
        password = flask.request.authorization['password']
        if not username or not password:
            return flask.jsonify({}), 400
    # return username
    # username = authenticate()'last_insert_rowid()'
    #initializing context dictionary
    context = {}
    #get postid from url
    postid = flask.request.args.get('postid')
    #HINT: sqlite3 provides a special function to retrieve
    #  the ID of the most recently inserted item: SELECT last_insert_rowid().
    connection = insta485.model.get_db()
    cur = connection.execute(
        #如果一个表中有 INTEGER PRIMARY KEY 列，则该列变成 ROWID 的别名。
        #the database is comments, so the primary key is comment id
        "SELECT last_insert_rowid()"
    )
    print("THE CUR IS")
    new_comment_id = cur.fetchall()[0]['last_insert_rowid()']
    print(new_comment_id)

    # get text from comment input box
    text = flask.request.get_json()['text']
    # if the comment is not inserted ????? how to know whether it is inserted or not 
    # then return 201

    # {
    #   "commentid": 8,
    #   "lognameOwnsThis": true,
    #   "owner": "awdeorio",
    #   "ownerShowUrl": "/users/awdeorio/",
    #   "text": "Comment sent from httpie",
    #   "url": "/api/v1/comments/8/"
    # }
    connection = insta485.model.get_db()
    cur = connection.execute(
        "INSERT INTO comments(owner,postid,text) VALUES"
        "(?,?,?)",
        (username, postid, text)
    )
    commentid = new_comment_id + 1
    context['commentid'] = commentid
    context['lognameOwnsThis'] = True
    context['owner'] = username
    context['text'] = text
    context['url'] = "/api/v1/comments/{}/".format(commentid)
    # input = 3
    # cur = connection.execute(
    #     # "INSERT INTO comments(owner,postid,text) VALUES"
    #     # "(?,?,?)",
    #     "SELECT * from comments WHERE postid == ?",
    #     (input,)
    # )
    # print(cur.fetchall())
    return flask.jsonify(**context), 201


# DELETE /api/v1/comments/<commentid>/
@insta485.app.route('/api/v1/comments/<commentid>/', methods=['DELETE'])
def delete_comment(commentid):
    auth = flask.request.authorization
    """delete a comment"""
    if 'username' not in flask.session and not auth:
        flask.abort(403)
    print("it is run")
    username = flask.session.get('username')
    if not username:
        username = flask.request.authorization['username']
        password = flask.request.authorization['password']
        if not username or not password:
            return flask.jsonify({}), 400
    # print(0)
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT owner FROM comments "
        "WHERE commentid == ?",
        (commentid,)
    )
    # print(1)
    comment_id_exist = cur.fetchall()
    if(len(comment_id_exist) == 0):
        # If the commentid does not exist, return 404.
        print(2)
        return flask.jsonify({}), 404
    else:
        # If the user doesn’t own the comment, return 403.
        owner = comment_id_exist[0]["owner"]
        print(3)
        if owner != username:
            return flask.jsonify({}), 403
        else:
            print(4)
            # Delete a comment. Include the ID of the comment in the URL.
            # Return 204 on success.
            connection.execute(
                "DELETE FROM comments "
                "WHERE commentid == ?",
                (commentid,)
            )
            connection.commit()
            return flask.jsonify({}), 204
