import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";

export default function Comment({comment,changeComment}){
  let comment_button;
  function deleteComment(){
    console.log("I am deleting !!!")
    changeComment(comment.url)
  }
  if (comment.lognameOwnsThis){
    comment_button = <button onClick={deleteComment}>delete</button>
  }
  return(
    <div>
      <strong><a href={comment.ownerShowUrl}>{comment.owner}</a></strong>{comment.text}
      {comment_button}
    </div>
  )
}

