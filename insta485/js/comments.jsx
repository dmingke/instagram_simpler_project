import React from "react";
import Comment from "./comment";


export default function Comments({comments, changeComment}){
    return(
        
        comments.map(comment =>{
            console.log("new added comments call this ")
            console.log(comment.commentid)
            return <Comment key={comment.id} comment={comment} changeComment={changeComment}/>
        })
    )   
}
