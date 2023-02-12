import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import Comment from "./comment";


export default function Comments({comments,changeComment}){
    return(
        
        comments.map(comment =>{
            console.log(comment)
            return <Comment key={comment.id} comment={comment} changeComment={changeComment}/>
        })
    )   
}
