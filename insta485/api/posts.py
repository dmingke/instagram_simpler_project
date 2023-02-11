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
        "url":  flask.request.full_path
    }
    return flask.jsonify(**context), 200

@insta485.app.route('/api/v1/posts/', methods=["GET"])
def get_post():
    # Return the 10 newest posts.
    # each post is made by a user which the logged in user follows 
    # or the post is made by the logged in user. 
    # When postid_lte is not specified, default to the most recent postid
    logname = flask.session.get('username')
    if not logname:
        logname = flask.request.authorization['username']
        password = flask.request.authorization['password']
        if not logname or not password:
            return flask.jsonify({}), 400
    size = flask.request.args.get("size", default=10, type=int)
    # size_if_user = flask.request.args.get("size", None)
    page = flask.request.args.get("page", default=0, type=int)
    # page_if_user = flask.request.args.get("page", None)
    if size < 0 or page < 0:
        return flask.jsonify({}), 400
    connection = insta485.model.get_db()
    total_postid = connection.execute(
        "SELECT postid FROM posts "
        "where owner == ? OR "
        "owner IN (SELECT username2 FROM following "
        "where username1 == ?)",
        (logname, logname, )
    ).fetchall()
    numPost = len(total_postid)
    newest = total_postid[numPost-1]['postid']
    postid_lte = flask.request.args.get("postid_lte", default=newest, type=int)
    # postid_if_user = flask.request.args.get("page"
    selected_postid = connection.execute(
        "SELECT postid,  ('/api/v1/posts/' || postid || '/') AS url FROM posts "
        "where owner == ? OR "
        "owner IN (SELECT username2 FROM following "
        "where username1 == ?) ORDER BY postid DESC "
        "LIMIT ? OFFSET ?",
        (logname, logname, size, size*page,)
    ).fetchall()
    # if not size_if_user and not page_if_user:

    if postid_lte == newest:
        if size*(page+1) <= numPost:
            # ?????????what is the page (the max)
            next = "/api/v1/posts/?size={}&page={}&postid_lte={}".format(size, page+1,newest)
        else:
            next = ""
    else:
        next = "/api/v1/posts/?size={}&page={}&postid_lte={}".format(size, page+1,postid_lte)
    results = list(selected_postid)

    context = {
        "next": next,
        "results": results,
        "url": flask.request.full_path.rstrip("?"),
    }
    return flask.jsonify(**context), 200


@insta485.app.route('/api/v1/posts/<int:postid_url_slug>/', methods=['GET'])
def get_post(postid_url_slug):
    #checking authorization...
    logname = flask.session.get('username')
    if not logname:
        logname = flask.request.authorization['username']
        password = flask.request.authorization['password']
        if not logname or not password:
            return flask.jsonify({}), 400

    #get post info from db
    connection = insta485.model.get_db()
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
        like_url = null
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
