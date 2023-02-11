import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import Post1 from "./post1"


export default function PostList({ postlist}){
    return postlist.map(post1 =>{
            return <Post1 post1={post1}></Post1>
        }
    )

    // console.log(postlist)
    // console.log("hhhhhhhhhhhhhhhhhhhhhhhhh")
    // return(
    //     <div>
    //         good
    //     </div>
    // )
}
