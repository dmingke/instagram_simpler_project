import React from "react";
import PropTypes from "prop-types";

export default function Comment({ comment, changeComment }) {
    let comment_button;
    function deleteComment() {
        changeComment(comment.url)
    }
    if (comment.lognameOwnsThis) {
        comment_button = <button type="submit" onClick={deleteComment}>delete</button>
    }
    return (
        <div>
            <strong><a href={comment.ownerShowUrl}>{comment.owner}</a></strong>{comment.text}
            {comment_button}
        </div>
    )
}

Comment.propTypes = {
    comment: PropTypes.object.isRequired,
    changeComment: PropTypes.func,
};
