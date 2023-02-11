import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
// import InfiniteScroll from "react-infinite-scroll-component";
// import moment from "moment";


// The parameter of this function is an object with a string called url inside it.
// url is a prop for the Post component.
export default function Post({ url }) {
  /* Display image and post owner of a single post */


  const [imgUrl, setImgUrl] = useState("");
  const [owner, setOwner] = useState("");
  const [created, setTime] = useState("");
  // const [ourl, setOurl] = useState("");
  const [oimg, setOimg] = useState("");
  const [purl, setPost] = useState("");


  useEffect(() => {
    // Declare a boolean flag that we can use to cancel the API request.
    let ignoreStaleRequest = false;


    // Call REST API to get the post's information
    fetch(url, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        // If ignoreStaleRequest was set to true, we want to ignore the results of the
        // the request. Otherwise, update the state to trigger a new render.
        if (!ignoreStaleRequest) {
          setImgUrl(data.results.imgUrl);
          setOwner(data.results.owner);
          setTime(data.results.created);
          // setOurl(data.results.ourl);
          setOimg(data.results.oimg);
          setPost(data.results.purl);
        }
      })
      .catch((error) => console.log(error));


    return () => {
      ignoreStaleRequest = true;
    };
  }, [url]);

  // let time = moment(created).fromNow();
  // let likes = <Moment=>
  // Render post image and post owner
  return (
    <div>
      <img src={imgUrl} alt="post_image" />
      <p>{owner}</p>
      {/* <img src={ourl} alt = "" /> */}
      <img src={oimg} alt = "" />
      <strong><a href={purl}>{created}</a></strong>
    </div>
  );
}

function componentDidMount(props) {
  const [state, setState] = useState({next:'', results:''});
  fetch(props.url, { credentials: 'same-origin' })
  .then((response) => {
    if (!response.ok) throw Error(response.statusText);
    return response.json();
  })
  .then((data) => {
    setState({
      next: data.next,
      results: data.results,
    });
  })
  .catch(error => console.log(error));


const posts = []
for (const [index, post] of state.results.entries()) {
  posts.push(<Post url={post.url} postid={post.postid} key={index} />)
}

function fetchData() {
  fetch(state.next, { credentials: 'same-origin' })
  .then((response) => {
    if (!response.ok) throw Error(response.statusText);
    return response.json();
  })
  .then((data) => {
    this.setState(prevState => ({
      next: data.next,
      results: prevState.results.concat(data.results),
    }));
  })
  .catch(error => console.log(error)); 
};
  return(
    <div className="container">
      <InfiniteScroll 
      dataLength={state.results.length} //This is important field to render the next data
      next={fetchData}
      hasMore={true}
      loader={<h4>Loading...</h4>}
      endMessage={
        <p style={{ textAlign: 'center' }}>
        </p>
      }
      >
    {posts}
    </InfiniteScroll>
    </div>
  );
}


Post.propTypes = {
  url: PropTypes.string.isRequired,
};
