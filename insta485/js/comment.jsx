import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";

export default function Comment({comment}){
  console.log(comment)
  return(
    <div>
      <strong><a href={comment.ownerShowUrl}>{comment.owner}</a></strong>{comment.text}
    </div>
  )
}
