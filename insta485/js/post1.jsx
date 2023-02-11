import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";


export default function Post1({id,post1}){

    let url = post1.url
    const [comments,setComments] = useState([])
    const [created,setCreated] = useState("")
    const [likes,setLikes] = useState({})
    const [owner,setOwner] = useState({})
    const [ownerImgUrl,setOwnerImg] = useState[""]
    const [imgUrl,setImgUrl] = useState[""]


    useEffect(()=>{
        fetch(url,{credentials:"same-origin"})
        .then((response) => {
            if (!response.ok) throw Error(response.statusText);
            return response.json();
          })
          .then((data) => {
            // If ignoreStaleRequest was set to true, we want to ignore the results of the
            // the request. Otherwise, update the state to trigger a new render.
            console.log(data)
            console.log("setdata================================")
            if (!ignoreStaleRequest) {
                setComments(data.comments)
                setCreated(data.created)
                setLikes(data.likes)
                setOwner(data.owner)
                setOwnerImg(data.ownerImgUrl)
                setImgUrl(data.imgUrl)
            }        
            
          })
          .catch((error) => console.log(error));

    },[post1]);
    
    return(
        <div>
           {/* <img></img> */}
           <img src={imgUrl} alt="picture1" class="picture1"></img>
        </div>
        
    )
}
