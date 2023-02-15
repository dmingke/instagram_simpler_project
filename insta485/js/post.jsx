import React, { useState, useEffect} from "react";
import PropTypes from "prop-types";
import InfiniteScroll from "react-infinite-scroll-component";
import moment from "moment";



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

function Post({props}){
      const [imgUrl, setImgUrl] = useState("");
      const [owner, setOwner] = useState("");
      const [ownerImgUrl, setOwnerImg] = useState("");
      const [comments,setComments] = useState([]);
      const [created,setCreated] = useState("");
      const [,setLikes] = useState({});
      const [ownerShowUrl, setOwnerUrl] = useState('');
      const [postShowUrl, setPostUrl] = useState('');
      const [liked, setLiked] = useState(false);
      const [likeURL, setLikeUrl] = useState('');
      const [postid,setPostid] = useState(0);
      const [comUrl,setCommentsUrl] = useState("");
      const [numLikes,setNumLikes] = useState(0);
      const [newCom,setNewAddedComment] = useState("");
      const [checkingCompleted,setCheckingCompleted] = useState(false);
      

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
          setCommentsUrl(data.comments_url)
          setLiked(data.likes.lognameLikesThis)
          setPostid(data.postid)
          setLikeUrl(data.likes.url)
          setNumLikes(data.likes.numLikes)
          setCheckingCompleted(true)
          }
        })
      .catch(error => console.log(error));
    
      return () => {
            ignoreStaleRequest = true;
        };
      }, [props]);
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
              setLikeUrl(() => {
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
            const requestOptions = {
              method: 'DELETE',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({})
            };
            fetch(link, requestOptions, { credentials: 'same-origin' })
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
        setLikeUrl(() =>{
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
        
        setLiked(()=>{
            const newlikenum = true;
            return newlikenum
        })
        })
    }
    }
    // end double click ^_^ 2

  function handleDelete(event){
    const deleteUrl = event.target.id;
    fetch(deleteUrl , { method: 'DELETE' })
      .then(() => 
      {
          fetch(props, { credentials: 'same-origin' })
          .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          return response.json();
          })
          .then((data) => {
              setComments(data.comments)
              setCommentsUrl(data.comments_url)
          })
          .catch(error => console.log(error));

      });
  }

  // var a =  Comments(){
  //   console.log("go to the comments function ")
    const showComments = comments.map((comment) =>{
        if(comment.lognameOwnsThis)
        return (
        <div key={comment.commentid}>
            <span className="comment-text"><strong><a href={comment.ownerShowUrl}>{comment.owner}</a></strong>{comment.text}</span>
            <button className="delete-comment-button" type="submit" onClick={handleDelete} id={comment.url}>delete</button>
            {/* <button>{comment.owner}</button> */}
        </div>
        )
        return(
        <div key={comment.commentid}>
          <span className="comment-text"><strong><a href={comment.ownerShowUrl}>{comment.owner}</a></strong>{comment.text}</span>
        </div>)
    })



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
                    setComments(prevComments =>[...prevComments,data]
                    )
                })
                setNewAddedComment("")      
            }
            
        }
        if (!checkingCompleted){
          return <p> please wait... </p>
        }

        return(
          <div>
          <a href={ownerShowUrl}><img src={ownerImgUrl} alt="men 1" width="50" height="46"/></a>
          <a href={ownerShowUrl}>{owner}</a>
          <a href={postShowUrl}>{time}</a>
          <div><img src={imgUrl} onDoubleClick={handleDoubleClick} alt="post_image" width="396" height="350"/></div>
          <p>{numLikes} {numLikes===1 ? "like" : "likes"}</p>
          <button type="submit" className="like-unlike-button" onClick={HandleLiked}>{liked ? 'unlike' : 'like'}</button>
          {/* <Comments key={comUrl} changeComment={changeComment}/> */}
          {showComments}
          <form className="comment-form">
          <input onChange={handleChange} onKeyDown={handleKeyDown} type="text" value={newCom}/>
          </form>
          </div>
        );
}



Posts.propTypes = {
  url: PropTypes.string.isRequired,
};
Post.propTypes = {
  props: PropTypes.string.isRequired
};
