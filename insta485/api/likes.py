"""REST API for likes."""
import flask
import insta485

@insta485.app.route('/api/v1/likes/', methods=['POST'])
def create_like():
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
    
    #initializing context dictionary
    context = {}

    #getting post id
    postid = flask.request.args.get('postid')
    print(postid)
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
        context['likeid'] = like_id
        context['url'] = url
        return flask.jsonify(**context), 201