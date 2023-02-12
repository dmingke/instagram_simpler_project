import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
// import InfiniteScroll from "react-infinite-scroll-component";
import moment from "moment";


// The parameter of this function is an object with a string called url inside it.
// url is a prop for the Post component.
export default function Posts({ url }) {
  /* Display image and post owner of a single post */
    // const [next, setNext] = useState('');
    const [results, setResult] = useState([]);
    useEffect(() => {
      // Declare a boolean flag that we can use to cancel the API request.
      let ignoreStaleRequest = false;
    fetch(url, { credentials: 'same-origin' })
    .then((response) => {
      if (!response.ok) throw Error(response.statusText);
      return response.json();
    })
    .then((data) => {
      if (!ignoreStaleRequest) {
        // setNext(data.next)
        setResult(data.results)
        }
      })
    .catch(error => console.log(error));
    return () => {
      ignoreStaleRequest = true;
    };
    }, [url]);
    return(
      <div>
        {results.map((result)=><Post props = {result.url}/>)}
      </div>
    );
}

function Post({props}){
      const [imgUrl, setImgUrl] = useState("");
      const [owner, setOwner] = useState("");
      const [ownerImgUrl, setOwnerImg] = useState("");
      const [comments,setComments] = useState([]);
      const [created,setCreated] = useState("");
      const [likes,setLikes] = useState({});
      const [ownerShowUrl, setOwnerUrl] = useState('');
      const [postShowUrl, setPostUrl] = useState('');
      

      useEffect(()=> {
        let ignoreStaleRequest = false;
      fetch(props, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        if (!ignoreStaleRequest) {
          // setNext(data.next)
          setComments(data.comments)
          setCreated(data.created)
          setLikes(data.likes)
          setOwner(data.owner)
          setOwnerImg(data.ownerImgUrl)
          setImgUrl(data.imgUrl)
          setOwnerUrl(data.ownerShowUrl)
          setPostUrl(data.postShowUrl)
          }
        })
      .catch(error => console.log(error));
    
      return () => {
            ignoreStaleRequest = true;
        };
      }, [props]);
      // let likes = 
      const time = moment(created).fromNow();
      return(
        <div>
           <a href={ownerShowUrl}><img src={ownerImgUrl} alt="men 1" width="50px" height="46px"/></a>
           <a href={ownerShowUrl}>{owner}</a>
          <a href={postShowUrl}>{time}</a>
          <div><img src={imgUrl} alt="post_image" width="396px" height="350px"/></div>
          {likes.numLikes} <p>likes</p>
          {/* {comments.map((comment)=><{result.url}/>)} */}
          <b><a href={comments.owner}>{comments.owner}</a></b>{comments.text}
        </div>
    );
      
}



Posts.propTypes = {
  url: PropTypes.string.isRequired,
};
Post.propTypes = {
  props: PropTypes.string.isRequired
};
