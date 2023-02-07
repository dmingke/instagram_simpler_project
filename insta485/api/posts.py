"""REST API for posts."""
import flask
import insta485

@insta485.app.route('/api/v1/posts/<int:postid_url_slug>/')
def get_post(postid_url_slug):
    #checking authorization...
    auth = flask.request.authorization
    if 'username' not in flask.session and not auth:
        flask.abort(403)
    username = None
    password = None
    if auth:
        username = flask.request.authorization['username']
        password = flask.request.authorization['password']
    else:
        username = flask.session.request['username']
        password = flask.session.request['password']

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

    #print(context)

    return flask.jsonify(**context)
