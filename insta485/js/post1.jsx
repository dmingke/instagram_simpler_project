import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";


export default function Post1({post1}){
    return(
        <div>
            <p>{post1.postid}</p>
            <p>{post1.url}</p>
        </div>
        
    )
}
