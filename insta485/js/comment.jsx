import React from "react";
import PropTypes from "prop-types";

export default function Comment({ comment, changeComment }) {
    let cbutton;
    function deleteComment() {
        changeComment(comment.url)
    }
    if (comment.lognameOwnsThis) {
        cbutton = <button className="delete-comment-button" type="submit" onClick={deleteComment}>delete</button>
    }
    return (
        <div>
            <span className="comment-text"><strong><a href={comment.ownerShowUrl}>{comment.owner}</a></strong>{comment.text}</span>
            {cbutton}
        </div>
    )
}

Comment.propTypes = {
    comment: PropTypes.object.isRequired,
    changeComment: PropTypes.func,
};
