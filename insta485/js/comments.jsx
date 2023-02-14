import React from "react";
import Comment from "./comment";


export default function Comments({comments, changeComment}){
    return(
        
        comments.map(comment =>
             <Comment key={comment.commentid} comment={comment} changeComment={changeComment}/>
        )
    )   
}
