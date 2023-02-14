import React, { useState, useEffect, useRef } from "react";
import PropTypes from "prop-types";
import InfiniteScroll from "react-infinite-scroll-component";
import moment from "moment";
import Comments from "./comments"


// The parameter of this function is an object with a string called url inside it.
// url is a prop for the Post component.
export default function Posts({ url }) {
  /* Display image and post owner of a single post */
    const [next, setNext] = useState("");
    const [results, setResult] = useState([]);
    const [hasMore, setHasMore] = useState(true);
    const [newResult, setNew] = useState([])
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
        setNext(data.next)
        setResult(data.results)
        setNew(data.results)
        }
      })
    .catch(error => console.log(error));
    return () => {
      ignoreStaleRequest = true;
    };
    }, [url]);
    
   
  const fetchData = async() => {
      if (next === "") {
        setHasMore(false)
        return;
      }
      fetch(next, { credentials: 'same-origin' })
      .then((response)=>{
        if (!response.ok) throw Error(response.statusText);
      return response.json(); 
      })
      .then((data) => {

        setNext(data.next)
        setNew(results.concat(data.results))

      }
    )
    .catch(error => console.log(error));

  }
  
    return(
      <InfiniteScroll
      dataLength={newResult.length}
      next={fetchData}
      hasMore={hasMore}
      loader={<h4>Loading...</h4>}
      >
      <div>
        {newResult.map((result)=><Post key={result.postid} props = {result.url}/>)}
      </div>
      </InfiniteScroll>
    );
}

function Post({props}) {
      const [imgUrl, setImgUrl] = useState("");
      const [owner, setOwner] = useState("");
      const [ownerImgUrl, setOwnerImg] = useState("");
      const [comments,setComments] = useState([]);
      const [created,setCreated] = useState("");
      const [likes,setLikes] = useState({});
      const [ownerShowUrl, setOwnerUrl] = useState('');
      const [postShowUrl, setPostUrl] = useState('');
      const [liked, setLiked] = useState(false);
      const [likeURL, setLikeUrl] = useState('');
      const [postid,setPostid] = useState(0);
      const [comUrl,setCommentsUrl] = useState("");
      const [numLikes,setNumLikes] = useState(0);
      const [newCom,setNewAddedComment] = useState("");
      

        // let ignoreStaleRequest = false;
      fetch(props, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {

          // setNext(data.next)
          setComments(data.comments)
          setCreated(data.created)
          setLikes(data.likes)
          setOwner(data.owner)
          setOwnerImg(data.ownerImgUrl)
          setImgUrl(data.imgUrl)
          setOwnerUrl(data.ownerShowUrl)
          setPostUrl(data.postShowUrl)
          setCommentsUrl(data.comUrl)
          setLiked(data.likes.lognameLikesThis)
          setPostid(data.postid)
          setLikeUrl(data.likes.url)
          setNumLikes(data.likes.numLikes)
          })
      .catch(error => console.log(error));
    


      const time = moment(created).fromNow();

      // like button section ^_^ 1
      function HandleLiked(){
          // const [likid, setlikeid] = useState(-1);
          if (!liked) {
            const requestOptions = {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({})
            };
            const linkPostLike = "/api/v1/likes/?postid=".concat(String(postid))
            fetch(linkPostLike, requestOptions,{ credentials: 'same-origin' })
            .then((response) => {
                if (!response.ok) throw Error(response.statusText);
                return response.json();
            })
            .then((data)=>{
              const tempurl = String(data.likeid)
              setLikeUrl(prevnum => {
                const newlikenum = "/api/v1/likes/".concat(tempurl.concat("/"));
                return newlikenum
              })
          
            })
            .then(()=>{
              
              setNumLikes(prevnum =>{
                const newlikenum = prevnum + 1;
                return newlikenum
              })
          
            })
          }
          else{
            const link = likeURL
            fetch(link, { credentials: 'same-origin' , method: 'DELETE'})
            .then(()=>{
                setNumLikes(prevnum =>{
                  const newlikenu = prevnum - 1;
                  return newlikenu
                })
            
            })
          }
          const likechange = !liked
          setLiked(likechange)
      }

      // end like button ^_^ 1

      // change when we comment
      function handleChange(event) {
        event.preventDefault()
        // var key = event.key;
        const newtext = event.target.value;
        const requestOptions = {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: newtext })
        };
        
        var key = event.key;
        if (key == "Enter") {
          fetch(comUrl, requestOptions,{ credentials: 'same-origin' })
          .then((response) => {
            if (!response.ok) throw Error(response.statusText);
            return response.json();
          })
          .then((data)=>{
              setComments(prevComments =>{
                return [...prevComments,data]
              })
          })
        }else{
          console.log(key)
    
        }
        

      }

     
    // started working on double click ^_^ 2
    function handleDoubleClick(){
    // console.log("double click successfully")
    if (!liked){
        console.log("double click successfully")
        const requestOptions = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
        };
        const linkPostLike = "/api/v1/likes/?postid=".concat(String(postid))
        fetch(linkPostLike, requestOptions,{ credentials: 'same-origin' })
        .then((response) => {
            if (!response.ok) throw Error(response.statusText);
            return response.json();
        })
        .then((data)=>{
        const tempurl = String(data.likeid)
        setLikeUrl(prevnum =>{
            const newlikenum = "/api/v1/likes/".concat(tempurl.concat("/"));
            return newlikenum
        })
    
        })
        .then(()=>{
        
        setNumLikes(prevnum =>{
            const newlikenum = prevnum + 1;
            return newlikenum
        })
        })
        .then(()=>{
        
        setLiked(prevnum =>{
            const newlikenum = true;
            return newlikenum
        })
        })
    }
    }
    // end double click ^_^ 2
    

  const changeComment = (commenturl)=>{

      fetch(commenturl, { method: 'DELETE' })
      .then(() => 
      {
          fetch(props, { credentials: 'same-origin' })
          .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          return response.json();
          })
          .then((data) => {
              setComments(data.comments)
              setCommentsUrl(data.comUrl)
          })
          .catch(error => console.log(error));

      });

  }


        function handleChange(event) {
            event.preventDefault()
            const newtext = event.target.value;
            setNewAddedComment(newtext);
        }

        function handleKeyDown(event){
            const requestOptions = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: newCom })
            };
            if (event.key === 'Enter') {
                fetch(comUrl, requestOptions,{ credentials: 'same-origin' })
                .then((response) => {
                    if (!response.ok) throw Error(response.statusText);
                    return response.json();
                })
                .then((data)=>{
                    setComments(prevComments =>{
                        return [...prevComments,data]
                    })
                })
                setNewAddedComment("")      
            }
            
        }

        return(
            <div>
            <a href={ownerShowUrl}><img src={ownerImgUrl} alt="men 1" width="50px" height="46px"/></a>
            <a href={ownerShowUrl}>{owner}</a>
            <a href={postShowUrl}>{time}</a>
            <div><img src={imgUrl} onDoubleClick={handleDoubleClick} alt="post_image" width="396px" height="350px"/></div>
            {numLikes} <p>likes</p>
            <button type="submit" onClick={HandleLiked}>{liked ? 'unlike' : 'like'}</button>
            <Comments key={comUrl} comments={comments} changeComment={changeComment}/>
            <input onChange={handleChange} onKeyDown={handleKeyDown} type="text" value={newCom}/>
            </div>
        );
}



Posts.propTypes = {
  url: PropTypes.string.isRequired,
};
Post.propTypes = {
  props: PropTypes.string.isRequired
};
